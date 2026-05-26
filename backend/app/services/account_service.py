"""
Account Service - Multi-account management with fingerprint isolation
"""
import os
import secrets
from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.models.account import TelegramAccount, AccountStatus
from app.core.telegram import telegram_manager
from app.core.config import settings


class AccountService:
    """Service for managing Telegram accounts with fingerprint isolation"""

    async def create_account(
        self,
        db: AsyncSession,
        phone: str,
        api_id: int,
        api_hash: str,
        session_name: str = None,
        is_default: bool = False,
        device_model: str = None,
        system_version: str = None,
        app_version: str = None,
        proxy_type: str = None,
        proxy_host: str = None,
        proxy_port: int = None,
    ) -> TelegramAccount:
        """Create a new Telegram account with isolated fingerprint"""

        # Check if phone already exists
        existing = await db.execute(
            select(TelegramAccount).where(TelegramAccount.phone == phone)
        )
        if existing.scalar_one_or_none():
            raise ValueError(f"Account with phone {phone} already exists")

        # Generate unique session name
        if not session_name:
            session_suffix = secrets.token_hex(4)
            session_name = f"account_{phone.replace('+', '')}_{session_suffix}"

        # If setting as default, remove default from others
        if is_default:
            result = await db.execute(select(TelegramAccount))
            for acc in result.scalars().all():
                acc.is_default = False

        # Generate random device fingerprint if not provided
        if not device_model or not system_version or not app_version:
            fingerprint = telegram_manager._generate_random_device_params()
            device_model = device_model or fingerprint["device_model"]
            system_version = system_version or fingerprint["system_version"]
            app_version = app_version or fingerprint["app_version"]

        account = TelegramAccount(
            phone=phone,
            api_id=api_id,
            api_hash=api_hash,
            session_name=session_name,
            is_default=is_default,
            status=AccountStatus.INACTIVE,
            device_model=device_model,
            system_version=system_version,
            app_version=app_version,
            proxy_type=proxy_type,
            proxy_host=proxy_host,
            proxy_port=proxy_port,
            proxy_enabled=bool(proxy_type and proxy_host and proxy_port),
        )

        db.add(account)
        await db.commit()
        await db.refresh(account)

        logger.info(f"Created Telegram account {phone} with fingerprint isolation")
        return account

    async def list_accounts(self, db: AsyncSession) -> List[TelegramAccount]:
        """Get all Telegram accounts"""
        result = await db.execute(select(TelegramAccount))
        return list(result.scalars().all())

    async def get_account(self, db: AsyncSession, account_id: int) -> Optional[TelegramAccount]:
        """Get account by ID"""
        result = await db.execute(
            select(TelegramAccount).where(TelegramAccount.id == account_id)
        )
        return result.scalar_one_or_none()

    async def activate_account(self, db: AsyncSession, account_id: int) -> TelegramAccount:
        """Activate a Telegram account (start session)"""
        account = await self.get_account(db, account_id)
        if not account:
            raise ValueError(f"Account {account_id} not found")

        try:
            # Get client with account's fingerprint isolation
            client = await telegram_manager.get_client_by_account(account)

            account.last_used_at = datetime.now(timezone.utc)
            await db.commit()
            logger.info(f"Activated account {account.phone} with isolated fingerprint")

        except Exception as e:
            account.status = AccountStatus.ERROR
            account.last_error = str(e)
            await db.commit()
            raise

        return account

    async def deactivate_account(self, db: AsyncSession, account_id: int) -> TelegramAccount:
        """Deactivate a Telegram account"""
        account = await self.get_account(db, account_id)
        if not account:
            raise ValueError(f"Account {account_id} not found")

        # Close client
        await telegram_manager.close_account_client(account_id)

        account.status = AccountStatus.INACTIVE
        await db.commit()

        logger.info(f"Deactivated account {account.phone}")
        return account

    async def delete_account(self, db: AsyncSession, account_id: int):
        """Delete a Telegram account"""
        account = await self.get_account(db, account_id)
        if not account:
            raise ValueError(f"Account {account_id} not found")

        # Close client first
        await telegram_manager.close_account_client(account_id)

        # Delete session files
        session_path = os.path.join(settings.SESSION_PATH, account.session_name)
        self._delete_session_files(session_path)

        await db.delete(account)
        await db.commit()

        logger.info(f"Deleted account {account.phone}")

    def _delete_session_files(self, session_path: str):
        """Delete all session files for an account"""
        if os.path.isfile(session_path):
            os.remove(session_path)

        # Also delete associated files
        for ext in ['.session', '.session-journal', '.json']:
            file_path = session_path + ext
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    logger.warning(f"Failed to delete {file_path}: {e}")

    async def get_default_account(self, db: AsyncSession) -> Optional[TelegramAccount]:
        """Get the default account"""
        result = await db.execute(
            select(TelegramAccount).where(TelegramAccount.is_default == True)
        )
        return result.scalar_one_or_none()

    async def update_account_fingerprint(
        self,
        db: AsyncSession,
        account_id: int,
        device_model: str = None,
        system_version: str = None,
        app_version: str = None,
    ) -> TelegramAccount:
        """Update account fingerprint (requires re-login)"""
        account = await self.get_account(db, account_id)
        if not account:
            raise ValueError(f"Account {account_id} not found")

        # Deactivate current session
        await telegram_manager.close_account_client(account_id)

        # Update fingerprint
        if device_model:
            account.device_model = device_model
        if system_version:
            account.system_version = system_version
        if app_version:
            account.app_version = app_version

        account.status = AccountStatus.INACTIVE
        await db.commit()

        logger.info(f"Updated fingerprint for account {account.phone}")
        return account


# Singleton instance
account_service = AccountService()
