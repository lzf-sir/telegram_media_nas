"""
Task Service - Business logic for download tasks
"""
import asyncio
import os
from datetime import datetime, timezone
from typing import Optional, List, Dict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.models.task import DownloadTask, TaskStatus
from app.models.file import DownloadedFile
from app.models.enums import FileExtension
from app.schemas.task import TaskCreate
from app.core.config import settings
from app.core.telegram import telegram_manager
from app.websocket.manager import manager
from app.tasks.download import process_download_task, cleanup_temp_files


class TaskService:
    """Service for managing download tasks"""

    def __init__(self):
        self._running_tasks: dict[int, asyncio.Task] = {}

    async def create_task(
        self,
        db: AsyncSession,
        task_data: TaskCreate,
    ) -> DownloadTask:
        """
        创建新的下载任务

        支持文件格式过滤和分类统计
        """
        task = DownloadTask(
            chat_id=task_data.chat_id,
            chat_title=task_data.chat_title,
            task_type=task_data.task_type,
            media_types=task_data.media_types,
            download_filter=task_data.download_filter,
            excluded_extensions=task_data.excluded_extensions or [],
            included_extensions=task_data.included_extensions or [],
            limit=task_data.limit,
            offset_id=task_data.offset_id,
            status=TaskStatus.PENDING,
            # 初始化统计字段
            stats_by_type={},
            stats_by_format={},
        )

        db.add(task)
        await db.commit()
        await db.refresh(task)

        logger.info(f"Created task {task.id} for chat {task_data.chat_id}")
        return task

    async def start_task(self, task_id: int):
        """Start a download task asynchronously"""
        if task_id in self._running_tasks:
            logger.warning(f"Task {task_id} is already running")
            return

        # Create async task
        async_task = asyncio.create_task(self._run_task(task_id))
        self._running_tasks[task_id] = async_task

    async def _run_task(self, task_id: int):
        """Run the download task"""
        from app.database import async_session_maker

        async with async_session_maker() as db:
            # Get task
            result = await db.execute(
                select(DownloadTask).where(DownloadTask.id == task_id)
            )
            task = result.scalar_one_or_none()

            if not task:
                logger.error(f"Task {task_id} not found")
                return

            # Update status
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now(timezone.utc)
            await db.commit()

            try:
                # Process the download
                await process_download_task(task, db)
            except Exception as e:
                logger.exception(f"Error processing task {task_id}: {e}")
                task.status = TaskStatus.FAILED
                await db.commit()
                await manager.send_task_complete(task_id, False, str(e))
            finally:
                # Clean up running task
                if task_id in self._running_tasks:
                    del self._running_tasks[task_id]

    async def cancel_task(self, task_id: int):
        """Cancel a running task"""
        if task_id in self._running_tasks:
            task = self._running_tasks[task_id]
            task.cancel()

            # Update status in DB
            from app.database import async_session_maker
            async with async_session_maker() as db:
                result = await db.execute(
                    select(DownloadTask).where(DownloadTask.id == task_id)
                )
                task_obj = result.scalar_one_or_none()
                if task_obj:
                    task_obj.status = TaskStatus.CANCELLED
                    await db.commit()

            await manager.send_task_complete(task_id, False, "Task cancelled")
        else:
            # Just update DB status
            from app.database import async_session_maker
            async with async_session_maker() as db:
                result = await db.execute(
                    select(DownloadTask).where(DownloadTask.id == task_id)
                )
                task_obj = result.scalar_one_or_none()
                if task_obj:
                    task_obj.status = TaskStatus.CANCELLED
                    await db.commit()

    async def retry_failed(self, db: AsyncSession, task_id: int) -> DownloadTask:
        """Create a new task retrying failed files from previous task"""
        # Get original task
        result = await db.execute(
            select(DownloadTask).where(DownloadTask.id == task_id)
        )
        original_task = result.scalar_one_or_none()

        if not original_task:
            raise ValueError(f"Task {task_id} not found")

        # Get failed message IDs
        failed_result = await db.execute(
            select(DownloadedFile.message_id).where(
                DownloadedFile.task_id == task_id,
            )
        )
        # For now, create a new task with same settings
        # TODO: Implement proper retry logic with specific message IDs

        new_task = DownloadTask(
            chat_id=original_task.chat_id,
            chat_title=original_task.chat_title,
            task_type=original_task.task_type,
            media_types=original_task.media_types,
            download_filter=original_task.download_filter,
            limit=original_task.limit,
            offset_id=original_task.offset_id,
            status=TaskStatus.PENDING,
        )

        db.add(new_task)
        await db.commit()
        await db.refresh(new_task)

        # Start the new task
        await self.start_task(new_task.id)

        return new_task

    async def update_progress(
        self,
        task_id: int,
        success: int = 0,
        failed: int = 0,
        skipped: int = 0,
        downloaded_bytes: int = 0,
        total_bytes: int = 0,
        current_file: str = None,
        current_file_progress: float = 0.0,
        download_speed: float = 0.0,
        eta_seconds: int = 0,
    ):
        """更新任务进度并通过 WebSocket 通知（含速度和 ETA）"""
        from app.database import async_session_maker

        async with async_session_maker() as db:
            result = await db.execute(
                select(DownloadTask).where(DownloadTask.id == task_id)
            )
            task = result.scalar_one_or_none()

            if task:
                task.success_count = success or task.success_count
                task.failed_count = failed or task.failed_count
                task.skipped_count = skipped
                task.downloaded_bytes = downloaded_bytes or task.downloaded_bytes
                task.total_bytes = total_bytes
                task.total_count = success + failed + skipped or task.total_count
                task.current_file_progress = current_file_progress
                task.updated_at = datetime.now(timezone.utc)
                await db.commit()

        # 发送 WebSocket 更新（含速度和 ETA）
        await manager.send_task_progress(
            task_id=task_id,
            status="running",
            current=task.total_count if task else 0,
            total=task.total_bytes if task else 0,
            success=success,
            failed=failed,
            downloaded_bytes=downloaded_bytes,
            total_bytes=total_bytes,
            current_file=current_file,
            current_file_progress=current_file_progress,
            download_speed=download_speed,
            eta_seconds=eta_seconds,
        )

    async def pause_task(self, task_id: int):
        """
        暂停正在运行的任务

        Args:
            task_id: 任务 ID
        """
        from app.database import async_session_maker

        async with async_session_maker() as db:
            result = await db.execute(
                select(DownloadTask).where(DownloadTask.id == task_id)
            )
            task = result.scalar_one_or_none()

            if task and task.status == TaskStatus.RUNNING:
                task.status = TaskStatus.PAUSED
                await db.commit()
                logger.info(f"Task {task_id} paused")

                # 通知 WebSocket
                await manager.send_task_progress(
                    task_id=task_id,
                    status="paused",
                    current=task.total_count or 0,
                    total=task.total_bytes or 0,
                    success=task.success_count or 0,
                    failed=task.failed_count or 0,
                    downloaded_bytes=task.downloaded_bytes or 0,
                )

    async def resume_task(self, task_id: int):
        """
        恢复已暂停的任务

        Args:
            task_id: 任务 ID
        """
        from app.database import async_session_maker

        async with async_session_maker() as db:
            result = await db.execute(
                select(DownloadTask).where(DownloadTask.id == task_id)
            )
            task = result.scalar_one_or_none()

            if task and task.status == TaskStatus.PAUSED:
                task.status = TaskStatus.PENDING
                await db.commit()
                logger.info(f"Task {task_id} resumed")

                # 重新启动任务
                await self.start_task(task_id)

    async def recover_running_tasks(self):
        """
        系统启动时恢复未完成的任务
        恢复状态为 RUNNING 或 PAUSED 的任务
        """
        from app.database import async_session_maker

        # 先清理临时文件
        await cleanup_temp_files()

        async with async_session_maker() as db:
            # 查找状态为 RUNNING 或 PAUSED 的任务
            result = await db.execute(
                select(DownloadTask).where(
                    DownloadTask.status.in_([
                        TaskStatus.RUNNING,
                        TaskStatus.PAUSED
                    ])
                )
            )
            tasks = result.scalars().all()

            logger.info(f"Found {len(tasks)} tasks to recover")

            for task in tasks:
                # 重置为 PENDING 状态
                task.status = TaskStatus.PENDING
                await db.commit()

                # 重新启动任务
                await self.start_task(task.id)
                logger.info(f"Recovered task {task.id} for chat {task.chat_id}")

            if tasks:
                logger.info(f"Successfully recovered {len(tasks)} tasks")


# Global task service instance
task_service = TaskService()
