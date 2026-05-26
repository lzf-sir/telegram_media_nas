"""
Forward Service - Message forwarding
"""
import asyncio
from typing import List
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.models.forward import ForwardTask
from app.models.task import TaskStatus
from app.models.account import TelegramAccount
from app.models.log import ActivityLog, LogLevel, LogType
from app.core.telegram import telegram_manager


class ForwardService:
    """Service for forwarding messages between chats"""

    async def create_task(
        self,
        db: AsyncSession,
        source_chat_id: str,
        destination_chat_id: str,
        source_chat_title: str = None,
        destination_chat_title: str = None,
        media_types: List[str] = None,
        download_filter: str = None,
        limit: int = 0,
        offset_id: int = 0,
        forward_with_caption: bool = True,
        copy_media: bool = False,
        account_id: int = None,
    ) -> ForwardTask:
        """Create a new forward task"""

        task = ForwardTask(
            source_chat_id=source_chat_id,
            source_chat_title=source_chat_title,
            destination_chat_id=destination_chat_id,
            destination_chat_title=destination_chat_title,
            media_types=media_types or [],
            download_filter=download_filter,
            limit=limit,
            offset_id=offset_id,
            forward_with_caption=1 if forward_with_caption else 0,
            copy_media=1 if copy_media else 0,
            account_id=account_id,
            status=TaskStatus.PENDING,
        )

        db.add(task)
        await db.commit()
        await db.refresh(task)

        logger.info(f"Created forward task {task.id}")
        return task

    async def start_task(self, db: AsyncSession, task_id: int):
        """Start a forward task asynchronously"""
        task = await db.get(ForwardTask, task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now(timezone.utc)
        await db.commit()

        # Run in background
        asyncio.create_task(self._run_forward_task(db, task))

    async def _run_forward_task(self, db: AsyncSession, task: ForwardTask):
        """Execute the forward task"""
        try:
            client = await telegram_manager.get_active_client()
            if not client:
                raise ValueError("No active Telegram client")

            # Get messages from source chat
            messages = await telegram_manager.get_chat_history(
                chat_id=task.source_chat_id,
                limit=task.limit if task.limit > 0 else 100,
                offset_id=task.offset_id,
            )

            task.total_count = len(messages)
            await db.commit()

            success_count = 0
            failed_count = 0
            skipped_count = 0

            for message in messages:
                try:
                    # Check if message has media (if filter is set)
                    if task.media_types:
                        media_type = self._get_media_type(message)
                        if media_type not in task.media_types:
                            skipped_count += 1
                            continue

                    # Forward or copy message
                    if task.copy_media:
                        # Copy as new message
                        await client.copy_message(
                            chat_id=task.destination_chat_id,
                            from_chat_id=task.source_chat_id,
                            message_id=message.id,
                        )
                    else:
                        # Forward original message
                        await client.forward_messages(
                            chat_id=task.destination_chat_id,
                            from_chat_id=task.source_chat_id,
                            message_ids=message.id,
                        )

                    success_count += 1

                    # Update progress
                    task.success_count = success_count
                    task.failed_count = failed_count
                    task.skipped_count = skipped_count
                    await db.commit()

                except Exception as e:
                    logger.error(f"Failed to forward message {message.id}: {e}")
                    failed_count += 1

            # Task complete
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now(timezone.utc)
            task.success_count = success_count
            task.failed_count = failed_count
            task.skipped_count = skipped_count
            await db.commit()

            logger.info(f"Forward task {task.id} completed: {success_count} forwarded")

        except Exception as e:
            logger.exception(f"Error in forward task {task.id}: {e}")
            task.status = TaskStatus.FAILED
            await db.commit()

            # Log error
            log = ActivityLog(
                level=LogLevel.ERROR,
                log_type=LogType.FORWARD,
                message=f"Forward task failed: {str(e)}",
                task_id=task.id,
            )
            db.add(log)
            await db.commit()

    def _get_media_type(self, message) -> str:
        """Get media type from message"""
        if message.audio:
            return "audio"
        elif message.document:
            return "document"
        elif message.photo:
            return "photo"
        elif message.video:
            return "video"
        elif message.voice:
            return "voice"
        elif message.video_note:
            return "video_note"
        elif message.animation:
            return "animation"
        return ""

    async def cancel_task(self, db: AsyncSession, task_id: int):
        """Cancel a forward task"""
        task = await db.get(ForwardTask, task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        task.status = TaskStatus.CANCELLED
        await db.commit()

    async def list_tasks(self, db: AsyncSession) -> List[ForwardTask]:
        """Get all forward tasks"""
        result = await db.execute(
            select(ForwardTask).order_by(ForwardTask.created_at.desc())
        )
        return list(result.scalars().all())


# Singleton instance
forward_service = ForwardService()
