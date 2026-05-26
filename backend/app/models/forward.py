"""
Forward Task Model
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.task import TaskStatus


class ForwardTask(Base):
    """Forward task model - forward messages from one chat to another"""

    __tablename__ = "forward_tasks"

    id = Column(Integer, primary_key=True, index=True)

    # Source and destination
    source_chat_id = Column(String, nullable=False, index=True)
    source_chat_title = Column(String)
    destination_chat_id = Column(String, nullable=False)
    destination_chat_title = Column(String)

    # Status
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.PENDING, nullable=False, index=True)

    # Progress tracking
    total_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    skipped_count = Column(Integer, default=0)

    # Configuration
    media_types = Column(JSON, default=list)
    download_filter = Column(String, nullable=True)
    limit = Column(Integer, default=0)
    offset_id = Column(Integer, default=0)

    # Forward options
    forward_with_caption = Column(Integer, default=1)  # 1 = yes, 0 = no
    copy_media = Column(Integer, default=0)  # 1 = copy as media, 0 = forward

    # Account to use
    account_id = Column(Integer, ForeignKey("telegram_accounts.id"), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "source_chat_id": self.source_chat_id,
            "source_chat_title": self.source_chat_title,
            "destination_chat_id": self.destination_chat_id,
            "destination_chat_title": self.destination_chat_title,
            "status": self.status.value if self.status else None,
            "total_count": self.total_count,
            "success_count": self.success_count,
            "failed_count": self.failed_count,
            "skipped_count": self.skipped_count,
            "media_types": self.media_types or [],
            "download_filter": self.download_filter,
            "limit": self.limit,
            "offset_id": self.offset_id,
            "forward_with_caption": self.forward_with_caption,
            "copy_media": self.copy_media,
            "account_id": self.account_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
