"""
Telegram Bot 管理器
用于处理 Bot 命令和消息
"""
import asyncio
from typing import Optional, Callable
from loguru import logger

try:
    from pyrogram import Client, filters
    from pyrogram.types import Message, BotCommand, BotCommandScopeAllPrivateChats, BotCommandScopeAllGroupChats
    from pyrogram.errors import FloodWait
    PYROGRAM_AVAILABLE = True
except ImportError:
    PYROGRAM_AVAILABLE = False
    logger.warning("Pyrogram 不可用，Bot 功能将无法使用")

from app.core.config import settings
from app.database import AsyncSession, async_session_maker
from app.services.settings_service import SettingsService


class TelegramBotManager:
    """Telegram Bot 管理器"""

    def __init__(self):
        self._bot_client: Optional[Client] = None
        self._is_running = False
        self._command_handlers = {}
        self._db: Optional[AsyncSession] = None

    async def get_db(self) -> AsyncSession:
        """获取数据库会话"""
        if not self._db:
            self._db = async_session_maker()
        return self._db

    async def start_bot(self, bot_token: str) -> bool:
        """
        启动 Bot 客户端

        Args:
            bot_token: Bot Token 从 @BotFather 获取

        Returns:
            是否启动成功
        """
        if not PYROGRAM_AVAILABLE:
            logger.error("Pyrogram 不可用，无法启动 Bot")
            return False

        try:
            # 创建 Bot 客户端
            self._bot_client = Client(
                "telegram_media_bot",
                bot_token=bot_token,
                in_memory=True,  # Bot 不需要会话文件
            )

            # 注册命令处理器
            self._register_handlers()

            # 启动 Bot
            await self._bot_client.start()
            self._is_running = True

            # 设置命令菜单
            await self._set_commands()

            logger.info("Telegram Bot 启动成功")
            return True

        except Exception as e:
            logger.error(f"启动 Bot 失败: {e}")
            return False

    async def stop_bot(self):
        """停止 Bot"""
        if self._bot_client and self._is_running:
            await self._bot_client.stop()
            self._is_running = False
            logger.info("Telegram Bot 已停止")

        # 关闭数据库连接
        if self._db:
            await self._db.close()
            self._db = None

    async def check_user_allowed(self, user_id: int, username: Optional[str] = None) -> bool:
        """
        检查用户是否被允许使用 Bot

        Args:
            user_id: Telegram 用户 ID
            username: Telegram 用户名（可选）

        Returns:
            是否允许使用
        """
        db = await self.get_db()
        try:
            return await SettingsService.is_user_in_whitelist(db, user_id, username)
        except Exception as e:
            logger.error(f"检查用户白名单失败: {e}")
            return True  # 出错时默认允许

    def _register_handlers(self):
        """注册命令处理器"""
        if not self._bot_client:
            return

        # /start - 开始使用
        @self._bot_client.on_message(filters.command("start"))
        async def start_command(client, message: Message):
            await message.reply_text(
                "👋 欢迎使用 Telegram Media NAS Bot！\n\n"
                "可用命令：\n"
                "/download - 下载当前聊天的媒体文件\n"
                "/status - 查看任务状态\n"
                "/cancel - 取消当前任务\n"
                "/help - 查看帮助"
            )

        # /download - 下载命令（需要白名单验证）
        @self._bot_client.on_message(filters.command("download"))
        async def download_command(client, message: Message):
            # 检查白名单
            if not await self.check_user_allowed(
                message.from_user.id,
                message.from_user.username
            ):
                await message.reply_text(
                    "❌ 您没有权限使用此命令。\n"
                    "请联系管理员添加您到白名单。",
                    quote=True
                )
                return

            # 触发下载任务
            chat = message.chat
            await message.reply_text(
                f"📥 开始下载聊天 `{chat.title or chat.first_name}` 的媒体文件...\n\n"
                "任务已创建，请稍候...",
                quote=True
            )

            # 这里可以触发创建下载任务的逻辑
            # TODO: 调用 task_service 创建任务

        # /status - 状态命令（需要白名单验证）
        @self._bot_client.on_message(filters.command("status"))
        async def status_command(client, message: Message):
            # 检查白名单
            if not await self.check_user_allowed(
                message.from_user.id,
                message.from_user.username
            ):
                await message.reply_text(
                    "❌ 您没有权限使用此命令。",
                    quote=True
                )
                return

            await message.reply_text(
                "📊 当前任务状态：\n\n"
                "暂无运行中的任务",
                quote=True
            )

        # /cancel - 取消命令（需要白名单验证）
        @self._bot_client.on_message(filters.command("cancel"))
        async def cancel_command(client, message: Message):
            # 检查白名单
            if not await self.check_user_allowed(
                message.from_user.id,
                message.from_user.username
            ):
                await message.reply_text(
                    "❌ 您没有权限使用此命令。",
                    quote=True
                )
                return

            await message.reply_text(
                "❌ 当前没有可取消的任务",
                quote=True
            )

        # /help - 帮助命令
        @self._bot_client.on_message(filters.command("help"))
        async def help_command(client, message: Message):
            help_text = (
                "📖 帮助文档\n\n"
                "【下载命令】\n"
                "/download - 下载当前聊天/频道的所有媒体\n"
                "回复 /download 到任意消息即可触发\n\n"
                "【过滤格式】\n"
                "可以在创建任务时指定要排除的文件格式\n"
                "例如：排除 .exe, .tmp 等文件\n\n"
                "【任务类型】\n"
                "• Bot 任务：通过 Bot 命令触发\n"
                "• 一次性任务：通过 Web 面板创建\n\n"
                "【文件去重】\n"
                "系统会自动计算 MD5，重复文件不会重复下载\n\n"
                "【权限说明】\n"
                "使用 Bot 命令需要管理员将您添加到白名单\n\n"
                "如有问题请联系管理员"
            )
            await message.reply_text(help_text)

        # 处理转发消息（需要白名单验证）
        @self._bot_client.on_message(filters.forwarded & ~filters.command(["start", "download", "status", "cancel", "help"]))
        async def handle_forward(client, message: Message):
            # 检查白名单
            if not await self.check_user_allowed(
                message.from_user.id,
                message.from_user.username
            ):
                await message.reply_text(
                    "❌ 您没有权限使用此功能。",
                    quote=True
                )
                return

            if message.forward_from:
                await message.reply_text(
                    f"📨 检测到转发消息\n"
                    f"来自: {message.forward_from.first_name or message.forward_from.title or '未知'}\n"
                    f"正在处理...",
                    quote=True
                )
                # TODO: 创建下载任务处理转发消息的媒体

    async def _set_commands(self):
        """设置 Bot 命令菜单"""
        commands = [
            BotCommand("start", "开始使用 Bot"),
            BotCommand("download", "下载当前聊天的媒体"),
            BotCommand("status", "查看任务状态"),
            BotCommand("cancel", "取消当前任务"),
            BotCommand("help", "查看帮助文档"),
        ]

        try:
            # 设置私聊命令
            await self._bot_client.set_bot_commands(
                commands,
                scope=BotCommandScopeAllPrivateChats()
            )
            # 设置群组命令
            await self._bot_client.set_bot_commands(
                commands,
                scope=BotCommandScopeAllGroupChats()
            )
            logger.info("Bot 命令菜单设置成功")
        except Exception as e:
            logger.warning(f"设置 Bot 命令失败: {e}")

    async def send_message(self, chat_id: int, text: str) -> bool:
        """
        发送消息到指定聊天

        Args:
            chat_id: 聊天 ID
            text: 消息文本

        Returns:
            是否发送成功
        """
        if not self._is_running or not self._bot_client:
            return False

        try:
            await self._bot_client.send_message(chat_id, text)
            return True
        except FloodWait as e:
            # 遇到 FloodWait 等待后重试
            await asyncio.sleep(e.value)
            return await self.send_message(chat_id, text)
        except Exception as e:
            logger.error(f"发送消息失败: {e}")
            return False

    async def send_task_progress(
        self,
        chat_id: int,
        task_id: int,
        status: str,
        success: int,
        failed: int,
        total: int
    ):
        """
        发送任务进度通知

        Args:
            chat_id: 聊天 ID
            task_id: 任务 ID
            status: 任务状态
            success: 成功数量
            failed: 失败数量
            total: 总数量
        """
        progress = (success + failed) / total * 100 if total > 0 else 0

        status_emoji = {
            "running": "⏳",
            "completed": "✅",
            "failed": "❌",
            "cancelled": "⏹️"
        }.get(status, "📋")

        message = (
            f"{status_emoji} 任务进度更新\n\n"
            f"任务 ID: {task_id}\n"
            f"状态: {status}\n"
            f"进度: {progress:.1f}%\n"
            f"成功: {success} | 失败: {failed} | 总计: {total}"
        )

        await self.send_message(chat_id, message)

    @property
    def is_running(self) -> bool:
        """Bot 是否正在运行"""
        return self._is_running

    @property
    def bot_client(self):
        """获取 Bot 客户端"""
        return self._bot_client


# 全局 Bot 管理器实例
bot_manager = TelegramBotManager()
