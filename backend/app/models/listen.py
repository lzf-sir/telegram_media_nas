"""
Listen Subscription Model - Real-time message monitoring
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, Text, ForeignKey
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class ListenStatus(str, enum.Enum):
    """Listen status enum"""
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"


class ListenSubscription(Base):
    """Real-time chat listening subscription for auto-downloading new messages"""

    __tablename__ = "listen_subscriptions"

    id = Column(Integer, primary_key=True, index=True)

    # Account to use for listening
    account_id = Column(Integer, ForeignKey("telegram_accounts.id"), nullable=False)

    # Chat to monitor
    chat_id = Column(String, nullable=False, index=True)
    chat_title = Column(String)

    # Status
    status = Column(SQLEnum(ListenStatus), default=ListenStatus.STOPPED, nullable=False)

    # Download settings
    media_types = Column(JSON, default=list)
    download_filter = Column(Text, nullable=True)
    file_formats = Column(JSON, default=dict)
    min_file_size = Column(Integer, nullable=True)  # in bytes
    max_file_size = Column(Integer, nullable=True)  # in bytes

    # Auto-forward settings
    auto_forward = Column(Boolean, default=False)
    forward_to_chat_id = Column(String, nullable=True)

    # Statistics
    total_listened = Column(Integer, default=0)
    total_downloaded = Column(Integer, default=0)
    total_forwarded = Column(Integer, default=0)

    # Tracking
    last_message_id = Column(Integer, default=0)
    last_processed_at = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "account_id": self.account_id,
            "chat_id": self.chat_id,
            "chat_title": self.chat_title,
            "status": self.status.value if self.status else None,
            "media_types": self.media_types or [],
            "download_filter": self.download_filter,
            "file_formats": self.file_formats or {},
            "min_file_size": self.min_file_size,
            "max_file_size": self.max_file_size,
            "auto_forward": self.auto_forward,
            "forward_to_chat_id": self.forward_to_chat_id,
            "total_listened": self.total_listened,
            "total_downloaded": self.total_downloaded,
            "total_forwarded": self.total_forwarded,
            "last_message_id": self.last_message_id,
            "last_processed_at": self.last_processed_at.isoformat() if self.last_processed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
