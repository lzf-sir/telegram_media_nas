"""
Telegram Account Model - Multi-account management
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy import Enum as SQLEnum
import enum

from app.database import Base


class AccountStatus(str, enum.Enum):
    """Account status enum"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    BANNED = "banned"
    ERROR = "error"


class TelegramAccount(Base):
    """Telegram account model for multi-account management"""

    __tablename__ = "telegram_accounts"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String, nullable=False, unique=True, index=True)

    # Telegram API credentials
    api_id = Column(Integer, nullable=False)
    api_hash = Column(String, nullable=False)

    # Account info
    user_id = Column(Integer, nullable=True)  # Telegram user ID
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)

    # Status
    status = Column(SQLEnum(AccountStatus), default=AccountStatus.INACTIVE, nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)

    # Session info
    session_name = Column(String, nullable=False, unique=True)
    last_used_at = Column(DateTime, nullable=True)

    # Device fingerprint for isolation
    device_model = Column(String, nullable=False, default="iPhone 14 Pro")
    system_version = Column(String, nullable=False, default="iOS 16.5")
    app_version = Column(String, nullable=False, default="10.2.0")
    lang_code = Column(String, nullable=False, default="en")
    lang_pack = Column(String, nullable=True)
    system_lang_code = Column(String, nullable=False, default="en-US")

    # Proxy config (optional per-account)
    proxy_type = Column(String, nullable=True)  # socks5, http
    proxy_host = Column(String, nullable=True)
    proxy_port = Column(Integer, nullable=True)
    proxy_username = Column(String, nullable=True)
    proxy_password = Column(String, nullable=True)
    proxy_enabled = Column(Boolean, default=False)

    # Error info
    last_error = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "phone": self.phone,
            "api_id": self.api_id,
            "api_hash": "***" if self.api_hash else None,
            "user_id": self.user_id,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "status": self.status.value if self.status else None,
            "is_default": self.is_default,
            "session_name": self.session_name,
            "last_used_at": self.last_used_at.isoformat() if self.last_used_at else None,
            "device_model": self.device_model,
            "system_version": self.system_version,
            "app_version": self.app_version,
            "lang_code": self.lang_code,
            "proxy_enabled": self.proxy_enabled,
            "proxy_type": self.proxy_type,
            "last_error": self.last_error,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def get_proxy_config(self):
        """Get proxy configuration for this account"""
        if not self.proxy_enabled or not self.proxy_type:
            return None
        return {
            "scheme": self.proxy_type,
            "hostname": self.proxy_host,
            "port": self.proxy_port,
            "username": self.proxy_username,
            "password": self.proxy_password,
        }

    def get_device_params(self):
        """Get device parameters for fingerprint isolation"""
        return {
            "device_model": self.device_model,
            "system_version": self.system_version,
            "app_version": self.app_version,
            "lang_code": self.lang_code,
            "lang_pack": self.lang_pack,
            "system_lang_code": self.system_lang_code,
        }
