"""
Listen Service - Real-time message monitoring
"""
import asyncio
from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger
from pyrogram import Client

from app.models.listen import ListenSubscription, ListenStatus
from app.models.account import TelegramAccount
from app.models.log import ActivityLog, LogLevel, LogType
from app.models.file import DownloadedFile
from app.core.config import settings


class ListenService:
    """Service for managing real-time chat listening"""

    def __init__(self):
        self._active_listeners: dict[int, asyncio.Task] = {}

    async def create_subscription(
        self,
        db: AsyncSession,
        account_id: int,
        chat_id: str,
        chat_title: str = None,
        media_types: List[str] = None,
        download_filter: str = None,
        auto_forward: bool = False,
        forward_to_chat_id: str = None,
    ) -> ListenSubscription:
        """Create a new listen subscription"""

        subscription = ListenSubscription(
            account_id=account_id,
            chat_id=chat_id,
            chat_title=chat_title,
            status=ListenStatus.STOPPED,
            media_types=media_types or [],
            download_filter=download_filter,
            auto_forward=auto_forward,
            forward_to_chat_id=forward_to_chat_id,
        )

        db.add(subscription)
        await db.commit()
        await db.refresh(subscription)

        logger.info(f"Created listen subscription for chat {chat_id}")
        return subscription

    async def start_listener(self, db: AsyncSession, subscription_id: int):
        """Start listening for new messages"""
        subscription = await db.get(ListenSubscription, subscription_id)
        if not subscription:
            raise ValueError(f"Subscription {subscription_id} not found")

        if subscription_id in self._active_listeners:
            logger.warning(f"Listener {subscription_id} is already running")
            return

        # Create async task for listening
        task = asyncio.create_task(self._listen_loop(db, subscription))
        self._active_listeners[subscription_id] = task

        subscription.status = ListenStatus.ACTIVE
        await db.commit()

    async def _listen_loop(self, db: AsyncSession, subscription: ListenSubscription):
        """Main listening loop"""
        from app.services.account_service import account_service

        try:
            # Get account
            account = await account_service.get_account(db, subscription.account_id)
            if not account:
                raise ValueError(f"Account {subscription.account_id} not found")

            # Get client
            from app.core.telegram import telegram_manager
            client = await telegram_manager.get_client(
                api_id=account.api_id,
                api_hash=account.api_hash,
                phone=account.phone,
                session_name=account.session_name,
            )

            # Subscribe to new messages
            async def message_handler(client, message):
                await self._handle_new_message(db, subscription, message)

            client.add_handler(message_handler)  # Simplified - actual handler setup more complex

            # Keep loop running
            while subscription.status == ListenStatus.ACTIVE:
                await asyncio.sleep(1)

                # Refresh from DB
                await db.refresh(subscription)

        except Exception as e:
            logger.exception(f"Error in listener {subscription.id}: {e}")
            subscription.status = ListenStatus.ERROR
            await db.commit()

            # Log error
            log = ActivityLog(
                level=LogLevel.ERROR,
                log_type=LogType.LISTEN,
                message=f"Listener error: {str(e)}",
                subscription_id=subscription.id,
            )
            db.add(log)
            await db.commit()

        finally:
            if subscription.id in self._active_listeners:
                del self._active_listeners[subscription.id]

    async def _handle_new_message(self, db, subscription, message):
        """Handle a new message"""
        subscription.total_listened += 1

        # Check if message has media
        if not message.media:
            return

        # Check media type filter
        media_type = self._get_media_type(message)
        if subscription.media_types and media_type not in subscription.media_types:
            return

        # Download media
        try:
            file_record = await self._download_media(message, subscription)
            if file_record:
                subscription.total_downloaded += 1
                db.add(file_record)

        except Exception as e:
            logger.error(f"Failed to download media from message {message.id}: {e}")

        # Forward if enabled
        if subscription.auto_forward and subscription.forward_to_chat_id:
            try:
                await message.forward(subscription.forward_to_chat_id)
                subscription.total_forwarded += 1
            except Exception as e:
                logger.error(f"Failed to forward message {message.id}: {e}")

        subscription.last_message_id = message.id
        subscription.last_processed_at = datetime.now(timezone.utc)
        await db.commit()

    def _get_media_type(self, message) -> Optional[str]:
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
        return None

    async def _download_media(self, message, subscription):
        """下载消息中的媒体文件，实现 MD5 去重"""
        import os
        import tempfile
        import shutil
        from datetime import datetime, timezone
        from pathlib import Path
        from app.tasks.download import calculate_md5, check_md5_exists, _get_file_extension

        media_type = self._get_media_type(message)
        if not media_type:
            return None

        # 获取文件信息
        media_obj = getattr(message, media_type, None)
        if not media_obj:
            return None

        file_size = getattr(media_obj, "file_size", 0)
        file_name = getattr(media_obj, "file_name", None)
        mime_type = getattr(media_obj, "mime_type", None)

        # 生成目标路径
        chat_title = message.chat.title if message.chat else str(message.chat.id)
        safe_chat_title = "".join(c for c in chat_title if c.isalnum() or c in (' ', '-', '_'))
        date_str = message.date.strftime("%Y_%m") if message.date else "unknown"
        file_extension = _get_file_extension(media_type, mime_type, file_name)

        if not file_name:
            file_name = f"{message.id}_{media_type}{file_extension}"
        elif not file_name.endswith(file_extension):
            file_name = f"{file_name}{file_extension}"

        download_dir = Path(settings.DOWNLOAD_PATH) / safe_chat_title / date_str / media_type
        download_dir.mkdir(parents=True, exist_ok=True)

        file_path = download_dir / file_name

        # 如果目标文件已存在，跳过
        if file_path.exists():
            logger.info(f"文件已存在: {file_path}")
            return None

        temp_file = None
        try:
            # 下载到临时文件
            with tempfile.NamedTemporaryFile(delete=False, dir=settings.TEMP_PATH) as tmp:
                temp_file = tmp.name

            # 使用消息自带的客户端直接下载（无需额外获取账号）
            downloaded_path = await message.download(file_name=temp_file)

            if not downloaded_path:
                logger.warning(f"下载失败: {file_name}")
                return None

            # 计算 MD5 并去重
            md5_hash = calculate_md5(temp_file)

            # 需要独立的数据库会话来检查 MD5
            from app.database import async_session_maker
            async with async_session_maker() as db:
                if await check_md5_exists(db, md5_hash):
                    logger.info(f"文件 MD5 重复，跳过: {file_name}")
                    os.unlink(temp_file)
                    return None

            # 移动到目标位置
            shutil.move(temp_file, file_path)
            logger.info(f"监听下载完成: {file_name} ({file_size} bytes)")

            # 创建文件记录
            file_record = DownloadedFile(
                task_id=None,  # 监听下载不关联具体任务
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
            )
            return file_record

        except Exception as e:
            logger.error(f"监听下载异常 {file_name}: {e}")
            return None
        finally:
            # 清理临时文件
            if temp_file and os.path.exists(temp_file):
                try:
                    os.unlink(temp_file)
                except Exception:
                    pass

    async def stop_listener(self, db: AsyncSession, subscription_id: int):
        """Stop a listener"""
        subscription = await db.get(ListenSubscription, subscription_id)
        if not subscription:
            raise ValueError(f"Subscription {subscription_id} not found")

        subscription.status = ListenStatus.STOPPED
        await db.commit()

        # Cancel task
        if subscription_id in self._active_listeners:
            self._active_listeners[subscription_id].cancel()
            del self._active_listeners[subscription_id]

    async def list_subscriptions(self, db: AsyncSession) -> List[ListenSubscription]:
        """Get all listen subscriptions"""
        result = await db.execute(select(ListenSubscription))
        return list(result.scalars().all())


# Singleton instance
listen_service = ListenService()
