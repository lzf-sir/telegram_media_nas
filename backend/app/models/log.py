"""
Activity Log Model
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Text, BigInteger
from sqlalchemy import Enum as SQLEnum
import enum

from app.database import Base


class LogLevel(str, enum.Enum):
    """Log level enum"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class LogType(str, enum.Enum):
    """Log type enum"""
    TASK = "task"
    DOWNLOAD = "download"
    FORWARD = "forward"
    LISTEN = "listen"
    ACCOUNT = "account"
    SYSTEM = "system"


class ActivityLog(Base):
    """Activity and operation log model"""

    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)

    # Log info
    level = Column(SQLEnum(LogLevel), default=LogLevel.INFO, nullable=False, index=True)
    log_type = Column(SQLEnum(LogType), nullable=False, index=True)

    # Related entity
    task_id = Column(Integer, nullable=True, index=True)
    chat_id = Column(String, nullable=True, index=True)
    message_id = Column(BigInteger, nullable=True)
    account_id = Column(Integer, nullable=True)

    # Message
    message = Column(Text, nullable=False)
    details = Column(Text, nullable=True)  # JSON string for additional details

    # Exception info (for errors)
    exception_type = Column(String, nullable=True)
    exception_message = Column(Text, nullable=True)
    stack_trace = Column(Text, nullable=True)

    # Timestamp
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "level": self.level.value if self.level else None,
            "log_type": self.log_type.value if self.log_type else None,
            "task_id": self.task_id,
            "chat_id": self.chat_id,
            "message_id": self.message_id,
            "account_id": self.account_id,
            "message": self.message,
            "details": self.details,
            "exception_type": self.exception_type,
            "exception_message": self.exception_message,
            "stack_trace": self.stack_trace,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
