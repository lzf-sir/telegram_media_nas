"""
系统设置模型 - 存储系统级配置
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Text

from app.database import Base


class SystemSetting(Base):
    """系统设置模型 - 键值对存储"""

    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(50), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=False)  # 改为 Text 类型支持更长内容
    value_type = Column(String(20), nullable=False, default="string")  # string, int, bool, json
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "key": self.key,
            "value": self.value,
            "value_type": self.value_type,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
