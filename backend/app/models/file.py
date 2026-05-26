"""
Downloaded File Model
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, BigInteger, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.database import Base


class MediaType(str):
    """Media type constants"""
    AUDIO = "audio"
    DOCUMENT = "document"
    PHOTO = "photo"
    VIDEO = "video"
    VOICE = "voice"
    VIDEO_NOTE = "video_note"
    ANIMATION = "animation"
    UNKNOWN = "unknown"


class DownloadedFile(Base):
    """Downloaded file model"""

    __tablename__ = "downloaded_files"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("download_tasks.id"), nullable=False, index=True)

    # Telegram message info
    message_id = Column(BigInteger, nullable=False)
    chat_id = Column(String, nullable=False, index=True)

    # File info
    file_name = Column(String, nullable=True)
    file_path = Column(String, nullable=False)
    file_size = Column(BigInteger, nullable=False)
    file_unique_id = Column(String, nullable=True)
    mime_type = Column(String, nullable=True)

    # 文件哈希 - 用于去重
    md5_hash = Column(String, nullable=False, index=True, unique=True)

    # Media info
    media_type = Column(String, nullable=False, index=True)
    duration = Column(Integer, nullable=True)  # For audio/video
    width = Column(Integer, nullable=True)  # For photo/video
    height = Column(Integer, nullable=True)  # For photo/video

    # Additional info
    caption = Column(Text, nullable=True)
    thumbnail_path = Column(String, nullable=True)

    # Timestamps
    downloaded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    # Relationships
    task = relationship("DownloadTask", back_populates="files")

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "task_id": self.task_id,
            "message_id": self.message_id,
            "chat_id": self.chat_id,
            "file_name": self.file_name,
            "file_path": self.file_path,
            "file_size": self.file_size,
            "file_unique_id": self.file_unique_id,
            "mime_type": self.mime_type,
            "media_type": self.media_type,
            "duration": self.duration,
            "width": self.width,
            "height": self.height,
            "caption": self.caption,
            "thumbnail_path": self.thumbnail_path,
            "md5_hash": self.md5_hash,
            "downloaded_at": self.downloaded_at.isoformat() if self.downloaded_at else None,
        }

    @property
    def file_extension(self):
        """Get file extension"""
        if self.file_name:
            return self.file_name.rsplit(".", 1)[-1].lower() if "." in self.file_name else ""
        return ""
