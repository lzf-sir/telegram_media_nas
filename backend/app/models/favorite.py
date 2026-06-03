"""
收藏聊天模型
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime

from app.database import Base


class FavoriteChat(Base):
    """收藏的聊天 ID"""
    __tablename__ = "favorite_chats"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(String, nullable=False, unique=True, index=True)
    chat_title = Column(String, nullable=True)
    note = Column(String, nullable=True)  # 自定义备注
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "chat_id": self.chat_id,
            "chat_title": self.chat_title,
            "note": self.note,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
