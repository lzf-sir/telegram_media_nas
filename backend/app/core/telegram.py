"""
Telegram Client Management with Fingerprint Isolation
"""
import asyncio
import os
import secrets
from datetime import datetime, timezone
from typing import Optional, Dict
from loguru import logger
import pyrogram
from pyrogram import Client
from pyrogram.types import Chat
from pyrogram.enums import ParseMode

from app.core.config import settings
from app.models.account import TelegramAccount, AccountStatus


class TelegramClientManager:
    """Manage Telegram client instances with fingerprint isolation"""

    def __init__(self):
        self._clients: Dict[str, Client] = {}
        self._active_client: Optional[Client] = None
        self._account_clients: Dict[int, Client] = {}  # account_id -> client mapping

    async def get_client(
        self,
        api_id: int = None,
        api_hash: str = None,
        phone: str = None,
        session_name: str = "telegram_media_nas",
        account: TelegramAccount = None,
    ) -> Client:
        """Get or create a Telegram client with fingerprint isolation"""

        # Use account fingerprint if provided
        if account:
            session_name = account.session_name
            proxy = account.get_proxy_config()
            device_params = account.get_device_params()
        else:
            # Generate random fingerprint for non-account clients
            proxy = None
            device_params = self._generate_random_device_params()

        # Check if client already exists
        if session_name in self._clients:
            client = self._clients[session_name]
            if not client.is_connected:
                await client.start()
            return client

        # Create new client with isolated fingerprint
        client = Client(
            name=os.path.join(settings.SESSION_PATH, session_name),
            api_id=api_id or settings.TELEGRAM_API_ID,
            api_hash=api_hash or settings.TELEGRAM_API_HASH,
            phone_number=phone,
            workdir=settings.SESSION_PATH,
            proxy=proxy,
            # Device fingerprint
            device_model=device_params.get("device_model", "iPhone 14 Pro"),
            system_version=device_params.get("system_version", "iOS 16.5"),
            app_version=device_params.get("app_version", "10.2.0"),
            lang_code=device_params.get("lang_code", "en"),
            lang_pack=device_params.get("lang_pack"),
            system_lang_code=device_params.get("system_lang_code", "en-US"),
            # Additional isolation
            ipv6=False,
            test_mode=False,
            bot_token=None,
            encrypted=True,
        )

        await client.start()
        self._clients[session_name] = client

        if account:
            self._account_clients[account.id] = client
            self._active_client = client
            # Update account info
            me = await client.get_me()
            account.user_id = me.id
            account.username = me.username
            account.first_name = me.first_name
            account.last_name = me.last_name
            account.last_used_at = datetime.now(timezone.utc)
            account.status = AccountStatus.ACTIVE
            account.last_error = None

        logger.info(f"Telegram client '{session_name}' started with fingerprint isolation")
        return client

    async def get_client_by_account(self, account: TelegramAccount) -> Client:
        """Get client for specific account"""
        if account.id in self._account_clients:
            client = self._account_clients[account.id]
            if client.is_connected:
                return client
            else:
                # Reconnect
                return await self.get_client(account=account)

        return await self.get_client(
            api_id=account.api_id,
            api_hash=account.api_hash,
            phone=account.phone,
            session_name=account.session_name,
            account=account,
        )

    async def get_active_client(self) -> Optional[Client]:
        """Get the active Telegram client"""
        if self._active_client:
            if not self._active_client.is_connected:
                await self._active_client.start()
            return self._active_client
        return None

    async def get_dialogs(self, client: Client = None, limit: int = 100) -> list[Chat]:
        """Get user's dialogs (chats)"""
        if not client:
            client = await self.get_active_client()
        if not client:
            raise ValueError("No active Telegram client")

        dialogs = []
        async for dialog in client.get_dialogs(limit=limit):
            dialogs.append(dialog)
        return dialogs

    async def get_chat_history(
        self,
        chat_id: int | str,
        limit: int = 100,
        offset_id: int = 0,
        client: Client = None,
    ) -> list:
        """Get chat history"""
        if not client:
            client = await self.get_active_client()
        if not client:
            raise ValueError("No active Telegram client")

        messages = []
        async for message in client.get_chat_history(
            chat_id,
            limit=limit,
            offset_id=offset_id,
        ):
            messages.append(message)
        return messages

    async def download_media(
        self,
        message,
        file_path: str,
        progress_callback=None,
        client: Client = None,
    ) -> Optional[str]:
        """Download media from a message"""
        if not client:
            client = await self.get_active_client()
        if not client:
            raise ValueError("No active Telegram client")

        return await client.download_media(
            message,
            file_name=file_path,
            progress=progress_callback,
        )

    def _generate_random_device_params(self) -> Dict[str, str]:
        """Generate random device parameters for fingerprint isolation"""
        # List of realistic device models
        device_models = [
            "iPhone 14 Pro", "iPhone 14", "iPhone 13 Pro", "iPhone 13",
            "iPhone 12 Pro", "iPhone 12", "iPhone 11 Pro", "iPhone 11",
            "Samsung Galaxy S23", "Samsung Galaxy S22", "Samsung Galaxy S21",
            "Google Pixel 7", "Google Pixel 6", "Xiaomi 13", "Xiaomi 12",
            "OnePlus 11", "OnePlus 10",
        ]

        # List of realistic system versions
        ios_versions = ["iOS 16.5", "iOS 16.4", "iOS 16.3", "iOS 15.7"]
        android_versions = [
            "Android 13", "Android 12", "Android 11",
            "MIUI 14", "OnePlus UI 13", "Pixel Experience"
        ]

        # List of realistic app versions
        app_versions = ["10.2.0", "10.1.0", "10.0.1", "9.9.0"]

        # Random selection
        import random
        device_model = random.choice(device_models)

        if "iPhone" in device_model or "iPad" in device_model:
            system_version = random.choice(ios_versions)
        else:
            system_version = random.choice(android_versions)

        lang_codes = ["en", "ru", "es", "de", "fr", "pt", "ar", "hi", "zh"]

        return {
            "device_model": device_model,
            "system_version": system_version,
            "app_version": random.choice(app_versions),
            "lang_code": random.choice(lang_codes),
            "lang_pack": None,
            "system_lang_code": random.choice(["en-US", "ru-RU", "es-ES", "de-DE"]),
        }

    async def close_client(self, session_name: str):
        """Close a specific client"""
        if session_name in self._clients:
            client = self._clients[session_name]
            if client.is_connected:
                await client.stop()
            del self._clients[session_name]

    async def close_account_client(self, account_id: int):
        """Close client for specific account"""
        if account_id in self._account_clients:
            client = self._account_clients[account_id]
            if client.is_connected:
                await client.stop()
            del self._account_clients[account_id]

    async def close_all(self):
        """Close all client connections"""
        for client in self._clients.values():
            if client.is_connected:
                await client.stop()
        self._clients.clear()
        self._account_clients.clear()
        self._active_client = None
        logger.info("All Telegram clients closed")


# Global instance
telegram_manager = TelegramClientManager()
