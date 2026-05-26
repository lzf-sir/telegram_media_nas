"""
Chat Schemas
"""
from typing import Optional, List
from pydantic import BaseModel, Field


class ChatSubscribe(BaseModel):
    """Schema for subscribing to a chat"""
    chat_id: str
    chat_title: str
    chat_username: Optional[str] = None
    chat_type: str
    media_types: Optional[List[str]] = None
    download_filter: Optional[str] = None
    auto_download: bool = False


class ChatResponse(BaseModel):
    """Schema for chat response"""
    id: int
    chat_id: str
    chat_title: str
    chat_username: Optional[str]
    chat_type: str
    is_active: bool
    media_types: Optional[List[str]]
    download_filter: Optional[str]
    auto_download: bool
    last_read_message_id: int
    total_downloaded: int
    created_at: Optional[str]
    updated_at: Optional[str]

    class Config:
        from_attributes = True


class ChatUpdate(BaseModel):
    """Schema for updating chat subscription"""
    is_active: Optional[bool] = None
    media_types: Optional[List[str]] = None
    download_filter: Optional[str] = None
    auto_download: Optional[bool] = None
