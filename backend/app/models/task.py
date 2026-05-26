"""
Download Task Model
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum, JSON, Float
from sqlalchemy.orm import relationship
import enum

from app.database import Base
from app.models.enums import TaskType


class TaskStatus(str, enum.Enum):
    """任务状态枚举"""
    PENDING = "pending"      # 等待执行
    RUNNING = "running"      # 执行中
    PAUSED = "paused"        # 已暂停（可恢复）
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"        # 失败
    CANCELLED = "cancelled"  # 已取消


class DownloadTask(Base):
    """Download task model"""

    __tablename__ = "download_tasks"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(String, nullable=False, index=True)
    chat_title = Column(String)
    task_type = Column(SQLEnum(TaskType), default=TaskType.ONETIME, nullable=False)
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.PENDING, nullable=False, index=True)

    # Progress tracking - 总体进度
    total_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    skipped_count = Column(Integer, default=0)
    downloaded_bytes = Column(Integer, default=0)
    total_bytes = Column(Integer, default=0)

    # 文件分类统计 - 按媒体类型分类的计数
    stats_by_type = Column(JSON, default=dict)  # {"audio": 10, "video": 5, ...}
    stats_by_format = Column(JSON, default=dict)  # 按扩展名统计 {".mp4": 15, ".jpg": 20}

    # 当前下载进度详情
    current_file_id = Column(Integer, nullable=True)  # 当前正在下载的文件消息ID
    current_file_name = Column(String, nullable=True)  # 当前文件名
    current_file_size = Column(Integer, nullable=True)  # 当前文件大小
    current_file_progress = Column(Float, default=0.0)  # 当前文件下载进度 0-100

    # Configuration
    media_types = Column(JSON, default=list)  # 要下载的媒体类型列表
    download_filter = Column(String, nullable=True)  # 下载过滤表达式
    excluded_extensions = Column(JSON, default=list)  # 排除的文件扩展名列表
    included_extensions = Column(JSON, default=list)  # 包含的文件扩展名列表（优先级高于排除）
    limit = Column(Integer, default=0)  # 最大下载数量，0 表示无限制
    offset_id = Column(Integer, default=0)  # 起始消息 ID

    # 断点续传相关
    last_processed_id = Column(Integer, nullable=True, index=True)  # 最后处理的消息ID
    processed_ids = Column(JSON, default=list)  # 已处理的消息ID列表（用于去重验证）

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    files = relationship("DownloadedFile", back_populates="task", cascade="all, delete-orphan")

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "chat_id": self.chat_id,
            "chat_title": self.chat_title,
            "task_type": self.task_type.value,
            "status": self.status.value,
            "total_count": self.total_count,
            "success_count": self.success_count,
            "failed_count": self.failed_count,
            "skipped_count": self.skipped_count,
            "downloaded_bytes": self.downloaded_bytes,
            "total_bytes": self.total_bytes,
            "stats_by_type": self.stats_by_type or {},
            "stats_by_format": self.stats_by_format or {},
            "current_file_id": self.current_file_id,
            "current_file_name": self.current_file_name,
            "current_file_size": self.current_file_size,
            "current_file_progress": self.current_file_progress,
            "media_types": self.media_types,
            "download_filter": self.download_filter,
            "excluded_extensions": self.excluded_extensions,
            "included_extensions": self.included_extensions,
            "limit": self.limit,
            "offset_id": self.offset_id,
            "last_processed_id": self.last_processed_id,
            "processed_ids": self.processed_ids or [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
