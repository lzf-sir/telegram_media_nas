"""
Celery/Asyncio Download Task with Resume Support
"""
import hashlib
import os
import time
import tempfile
import glob
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional, List
from loguru import logger
from pyrogram.types import Message
from sqlalchemy import select

from app.models.task import DownloadTask, TaskStatus
from app.models.file import DownloadedFile, MediaType
from app.services.task_service import task_service
from app.core.config import settings
from app.core.telegram import telegram_manager


def calculate_md5(file_path: str) -> str:
    """
    计算文件的 MD5 哈希值

    Args:
        file_path: 文件路径

    Returns:
        MD5 哈希值（32位十六进制字符串）
    """
    md5_hash = hashlib.md5()
    with open(file_path, 'rb') as f:
        # 分块读取文件，避免大文件占用过多内存
        for chunk in iter(lambda: f.read(8192), b''):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()


async def check_md5_exists(db, md5_hash: str) -> bool:
    """
    检查数据库中是否已存在指定 MD5 的文件

    Args:
        db: 数据库会话
        md5_hash: MD5 哈希值

    Returns:
        True 如果已存在，False 如果不存在
    """
    result = await db.execute(
        select(DownloadedFile).where(DownloadedFile.md5_hash == md5_hash)
    )
    return result.scalar_one_or_none() is not None


async def cleanup_temp_files():
    """清理临时目录中的孤儿文件"""
    try:
        temp_path = Path(settings.TEMP_PATH)
        if not temp_path.exists():
            return

        # 查找所有临时文件
        temp_files = list(temp_path.glob("tmp*"))

        for temp_file in temp_files:
            try:
                # 检查文件是否超过1小时未修改
                file_time = temp_file.stat().st_mtime
                if time.time() - file_time > 3600:
                    temp_file.unlink()
                    logger.info(f"Cleaned up orphaned temp file: {temp_file}")
            except Exception as e:
                logger.warning(f"Failed to cleanup temp file {temp_file}: {e}")

    except Exception as e:
        logger.error(f"Error during temp file cleanup: {e}")


async def process_download_task(task: DownloadTask, db):
    """
    Process a download task - fetch messages and download media
    支持断点续传

    Args:
        task: The download task to process
        db: Database session
    """
    logger.info(f"Starting download task {task.id} for chat {task.chat_id}")

    try:
        client = await telegram_manager.get_active_client()
        if not client:
            raise ValueError("No active Telegram client. Please configure Telegram first.")

        # 从断点恢复：使用 last_processed_id 或 offset_id
        start_id = task.last_processed_id or task.offset_id

        # 初始化已处理ID列表
        if not task.processed_ids:
            task.processed_ids = []

        logger.info(f"Task {task.id} starting from message_id: {start_id}, "
                   f"already processed: {len(task.processed_ids)} messages")

        # Get chat history
        messages = await telegram_manager.get_chat_history(
            chat_id=task.chat_id,
            limit=task.limit if task.limit > 0 else 100,
            offset_id=start_id,
        )

        # 过滤掉已处理的消息
        messages = [m for m in messages if m.id not in task.processed_ids]

        task.total_count = len(messages) + len(task.processed_ids)
        await db.commit()

        success_count = task.success_count or 0
        failed_count = task.failed_count or 0
        skipped_count = task.skipped_count or 0
        downloaded_bytes = task.downloaded_bytes or 0
        total_bytes = task.total_bytes or 0

        checkpoint_counter = 0  # 检查点计数器

        for message in messages:
            # 定期刷新任务状态检查暂停/取消
            if checkpoint_counter % 5 == 0:
                result = await db.execute(
                    select(DownloadTask).where(DownloadTask.id == task.id)
                )
                task = result.scalar_one()

            # 检查任务状态
            if task.status == TaskStatus.CANCELLED:
                logger.info(f"Task {task.id} was cancelled")
                # 保存断点
                if message.id:
                    task.last_processed_id = message.id
                await db.commit()
                return

            if task.status == TaskStatus.PAUSED:
                logger.info(f"Task {task.id} was paused")
                # 保存断点
                if message.id:
                    task.last_processed_id = message.id
                await db.commit()
                # 发送暂停通知
                from app.websocket.manager import manager
                await manager.send_task_complete(task.id, False, "Task paused")
                return

            checkpoint_counter += 1

            try:
                # Determine media type
                media_type = _get_media_type(message)
                if not media_type:
                    skipped_count += 1
                    # 记录已处理的消息ID
                    if message.id:
                        task.processed_ids.append(message.id)
                    continue

                # Check if media type is in filter
                if task.media_types and media_type not in task.media_types:
                    skipped_count += 1
                    # 记录已处理的消息ID
                    if message.id:
                        task.processed_ids.append(message.id)
                    continue

                # Get file extension for format filtering
                media_obj = getattr(message, media_type, None)
                file_name = getattr(media_obj, "file_name", None) if media_obj else None
                file_ext = _get_file_extension(media_type, None, file_name)

                # 检查文件格式是否被过滤
                excluded_exts = task.excluded_extensions or []
                included_exts = task.included_extensions or []

                if not should_download_file(file_ext, excluded_exts, included_exts):
                    logger.info(f"Skipping {file_name} - extension {file_ext} is filtered")
                    skipped_count += 1

                    # 记录已处理
                    if message.id:
                        task.processed_ids.append(message.id)

                    # 更新统计
                    update_task_stats(task, media_type, file_ext)
                    await db.commit()
                    continue

                # Download the media
                file_record, file_size = await download_media_from_message(
                    message, task.id, media_type, client, db, task
                )

                if file_record:
                    db.add(file_record)
                    downloaded_bytes += file_size
                    success_count += 1

                    # 更新文件分类统计
                    update_task_stats(task, media_type, file_ext)

                    # 记录已处理的消息ID
                    if message.id:
                        task.processed_ids.append(message.id)

                    # 定期保存断点（每处理10个消息）
                    if success_count % 10 == 0:
                        task.last_processed_id = message.id
                        await db.commit()

                    # Update progress
                    await task_service.update_progress(
                        task_id=task.id,
                        success=success_count,
                        failed=failed_count,
                        skipped=skipped_count,
                        downloaded_bytes=downloaded_bytes,
                        current_file=file_record.file_name,
                        stats_by_type=task.stats_by_type,
                        stats_by_format=task.stats_by_format,
                    )
                else:
                    skipped_count += 1
                    # 记录已处理
                    if message.id:
                        task.processed_ids.append(message.id)

            except Exception as e:
                logger.error(f"Error processing message {message.id}: {e}")
                failed_count += 1
                # 记录已处理但失败
                if message.id:
                    task.processed_ids.append(message.id)

        # Update final status
        result = await db.execute(
            select(DownloadTask).where(DownloadTask.id == task.id)
        )
        task = result.scalar_one()
        task.status = TaskStatus.COMPLETED
        task.success_count = success_count
        task.failed_count = failed_count
        task.skipped_count = skipped_count
        task.downloaded_bytes = downloaded_bytes
        task.completed_at = datetime.utcnow()
        # 完成时清除断点数据
        task.last_processed_id = None
        task.processed_ids = []
        await db.commit()

        logger.info(
            f"Task {task.id} completed: {success_count} success, "
            f"{failed_count} failed, {skipped_count} skipped"
        )

        from app.websocket.manager import manager
        await manager.send_task_complete(task.id, True)

    except Exception as e:
        logger.exception(f"Fatal error in task {task.id}: {e}")
        result = await db.execute(
            select(DownloadTask).where(DownloadTask.id == task.id)
        )
        task = result.scalar_one()
        task.status = TaskStatus.FAILED
        # 失败时保留断点数据以便重试
        await db.commit()

        from app.websocket.manager import manager
        await manager.send_task_complete(task.id, False, str(e))


def _get_media_type(message: Message) -> Optional[str]:
    """Get media type from a message"""
    if message.audio:
        return MediaType.AUDIO
    elif message.document:
        return MediaType.DOCUMENT
    elif message.photo:
        return MediaType.PHOTO
    elif message.video:
        return MediaType.VIDEO
    elif message.voice:
        return MediaType.VOICE
    elif message.video_note:
        return MediaType.VIDEO_NOTE
    elif message.animation:
        return MediaType.ANIMATION
    return None


async def download_media_from_message(
    message: Message,
    task_id: int,
    media_type: str,
    client,
    db,
    task: DownloadTask,
) -> tuple[Optional[DownloadedFile], int]:
    """
    Download media from a message and save file record
    实现 MD5 去重：先下载到临时位置，计算 MD5 后检查数据库，决定是否保留

    Args:
        message: Telegram 消息
        task_id: 任务 ID
        media_type: 媒体类型
        client: Telegram 客户端
        db: 数据库会话
        task: 任务对象（用于更新进度）

    Returns:
        tuple: (DownloadedFile record, file_size) 或 (None, 0) 如果跳过
    """
    # 获取文件信息
    media_obj = getattr(message, media_type, None)
    if not media_obj:
        return None, 0

    file_size = getattr(media_obj, "file_size", 0)
    file_name = getattr(media_obj, "file_name", None)
    mime_type = getattr(media_obj, "mime_type", None)

    # 生成文件路径
    chat_title = message.chat.title if message.chat else str(message.chat.id)
    safe_chat_title = "".join(c for c in chat_title if c.isalnum() or c in (' ', '-', '_'))

    date_str = message.date.strftime("%Y_%m") if message.date else "unknown"
    file_extension = _get_file_extension(media_type, mime_type, file_name)

    if not file_name:
        file_name = f"{message.id}_{media_type}{file_extension}"
    elif not file_name.endswith(file_extension):
        file_name = f"{file_name}{file_extension}"

    # 创建目标目录
    download_dir = Path(settings.DOWNLOAD_PATH) / safe_chat_title / date_str / media_type
    download_dir.mkdir(parents=True, exist_ok=True)

    file_path = download_dir / file_name

    # 更新当前下载的文件信息
    task.current_file_id = message.id
    task.current_file_name = file_name
    task.current_file_size = file_size
    task.current_file_progress = 0.0

    # 先下载到临时位置
    temp_file = None
    try:
        # 创建临时文件
        with tempfile.NamedTemporaryFile(delete=False, dir=settings.TEMP_PATH) as tmp:
            temp_file = tmp.name

        start_time = time.time()
        last_progress_update = start_time

        def progress_callback(current, total):
            """下载进度回调 - 更新任务进度"""
            nonlocal last_progress_update

            # 更新当前文件进度
            if total > 0:
                progress = (current / total) * 100
                task.current_file_progress = progress

                # 每秒更新一次数据库，避免频繁写入
                now = time.time()
                if now - last_progress_update >= 1.0:
                    last_progress_update = now
                    # 异步更新进度（不等待）
                    asyncio.create_task(task_service.update_progress(
                        task_id=task.id,
                        current_file=file_name,
                        current_file_progress=progress,
                    ))

        # 下载到临时文件
        downloaded_path = await client.download_media(
            message,
            file_name=temp_file,
            progress=progress_callback if file_size > 10 * 1024 * 1024 else None,
        )

        if not downloaded_path:
            logger.warning(f"Failed to download {file_name}")
            task.current_file_progress = 0.0
            return None, 0

        # 计算文件的 MD5 哈希值
        md5_hash = calculate_md5(temp_file)
        logger.info(f"File {file_name} MD5: {md5_hash}")

        # 检查数据库中是否已存在该 MD5
        if await check_md5_exists(db, md5_hash):
            logger.info(f"File with MD5 {md5_hash} already exists, skipping {file_name}")
            # 删除临时文件
            os.unlink(temp_file)
            task.current_file_progress = 0.0
            return None, 0

        # MD5 不存在，移动文件到目标位置
        import shutil
        shutil.move(temp_file, file_path)

        download_time = time.time() - start_time
        logger.info(f"Downloaded {file_name} ({file_size} bytes) in {download_time:.1f}s")

        task.current_file_progress = 100.0

        return (
            DownloadedFile(
                task_id=task_id,
                message_id=message.id,
                chat_id=str(message.chat.id),
                file_name=file_name,
                file_path=str(file_path),
                file_size=file_size,
                file_unique_id=getattr(media_obj, "file_unique_id", None),
                mime_type=mime_type,
                media_type=media_type,
                duration=getattr(media_obj, "duration", None),
                width=getattr(media_obj, "width", None),
                height=getattr(media_obj, "height", None),
                caption=message.caption or message.text,
                md5_hash=md5_hash,
            ),
            file_size,
        )

    except Exception as e:
        logger.error(f"Failed to download {file_name}: {e}")
        task.current_file_progress = 0.0
        # 清理临时文件
        if temp_file and os.path.exists(temp_file):
            try:
                os.unlink(temp_file)
            except Exception:
                pass

    return None, 0


def _get_file_extension(media_type: str, mime_type: Optional[str], file_name: Optional[str]) -> str:
    """Get file extension from media type, mime type or file name"""
    if file_name and "." in file_name:
        return "." + file_name.rsplit(".", 1)[-1].lower()

    if mime_type:
        return "." + mime_type.split("/")[-1]

    # Default extensions by media type
    extensions = {
        MediaType.AUDIO: ".mp3",
        MediaType.DOCUMENT: ".bin",
        MediaType.PHOTO: ".jpg",
        MediaType.VIDEO: ".mp4",
        MediaType.VOICE: ".ogg",
        MediaType.VIDEO_NOTE: ".mp4",
        MediaType.ANIMATION: ".mp4",
    }

    return extensions.get(media_type, ".bin")


def should_download_file(
    file_ext: str,
    excluded_exts: List[str],
    included_exts: List[str]
) -> bool:
    """
    判断文件是否应该下载（根据扩展名过滤）

    Args:
        file_ext: 文件扩展名（包含点号，如 .mp4）
        excluded_exts: 排除的扩展名列表
        included_exts: 包含的扩展名列表

    Returns:
        True 如果应该下载，False 如果应该跳过
    """
    # 标准化扩展名格式
    if not file_ext.startswith('.'):
        file_ext = '.' + file_ext
    file_ext = file_ext.lower()

    # 如果有包含列表，只下载在列表中的文件
    if included_exts:
        included_normalized = [ext.lower() if ext.startswith('.') else f'.{ext.lower()}' for ext in included_exts]
        return file_ext in included_normalized

    # 如果有排除列表，排除列表中的文件
    if excluded_exts:
        excluded_normalized = [ext.lower() if ext.startswith('.') else f'.{ext.lower()}' for ext in excluded_exts]
        return file_ext not in excluded_normalized

    # 没有过滤规则，全部下载
    return True


def update_task_stats(
    task: DownloadTask,
    media_type: str,
    file_ext: str
):
    """
    更新任务的文件分类统计

    Args:
        task: 任务对象
        media_type: 媒体类型
        file_ext: 文件扩展名
    """
    # 初始化统计字典
    if not task.stats_by_type:
        task.stats_by_type = {}
    if not task.stats_by_format:
        task.stats_by_format = {}

    # 按媒体类型统计
    task.stats_by_type[media_type] = task.stats_by_type.get(media_type, 0) + 1

    # 按扩展名统计
    file_ext = file_ext.lower()
    task.stats_by_format[file_ext] = task.stats_by_format.get(file_ext, 0) + 1
