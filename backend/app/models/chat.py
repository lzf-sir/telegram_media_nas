"""
Chat Subscription Model
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, Text
from sqlalchemy import Enum as SQLEnum

from app.database import Base
import enum


class ChatType(str, enum.Enum):
    """Chat type enum"""
    PRIVATE = "private"
    GROUP = "group"
    SUPERGROUP = "supergroup"
    CHANNEL = "channel"


class ChatSubscription(Base):
    """Chat subscription model"""

    __tablename__ = "chat_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(String, nullable=False, unique=True, index=True)
    chat_title = Column(String, nullable=False)
    chat_username = Column(String, nullable=True)
    chat_type = Column(SQLEnum(ChatType), nullable=False)

    # Subscription settings
    is_active = Column(Boolean, default=True, nullable=False)

    # Download configuration
    media_types = Column(JSON, default=list)
    download_filter = Column(Text, nullable=True)
    file_formats = Column(JSON, default=dict)

    # Auto-download settings
    auto_download = Column(Boolean, default=False)
    auto_forward_chat_id = Column(String, nullable=True)

    # Tracking
    last_read_message_id = Column(Integer, default=0)
    total_downloaded = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "chat_id": self.chat_id,
            "chat_title": self.chat_title,
            "chat_username": self.chat_username,
            "chat_type": self.chat_type.value if self.chat_type else None,
            "is_active": self.is_active,
            "media_types": self.media_types or [],
            "download_filter": self.download_filter,
            "file_formats": self.file_formats or {},
            "auto_download": self.auto_download,
            "auto_forward_chat_id": self.auto_forward_chat_id,
            "last_read_message_id": self.last_read_message_id,
            "total_downloaded": self.total_downloaded,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
