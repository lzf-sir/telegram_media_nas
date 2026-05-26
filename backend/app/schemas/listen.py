"""
Listen Subscription Schemas
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class ListenSubscriptionCreate(BaseModel):
    """Schema for creating a listen subscription"""
    account_id: int = Field(..., description="Telegram account ID to use")
    chat_id: str = Field(..., description="Chat ID to monitor")
    chat_title: Optional[str] = None
    media_types: Optional[List[str]] = Field(None, description="Media types to download")
    download_filter: Optional[str] = None
    auto_forward: bool = Field(False, description="Auto-forward new messages")
    forward_to_chat_id: Optional[str] = Field(None, description="Chat ID to forward to")


class ListenSubscriptionResponse(BaseModel):
    """Schema for listen subscription response"""
    id: int
    account_id: int
    chat_id: str
    chat_title: str | None
    status: str
    media_types: List[str] | None
    download_filter: str | None
    file_formats: dict | None
    min_file_size: int | None
    max_file_size: int | None
    auto_forward: bool
    forward_to_chat_id: str | None
    total_listened: int
    total_downloaded: int
    total_forwarded: int
    last_message_id: int
    last_processed_at: str | None
    created_at: str | None
    updated_at: str | None

    class Config:
        from_attributes = True
