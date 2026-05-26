"""
Forward Task Schemas
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class ForwardTaskCreate(BaseModel):
    """Schema for creating a forward task"""
    source_chat_id: str = Field(..., description="Source chat ID to forward from")
    destination_chat_id: str = Field(..., description="Destination chat ID to forward to")
    source_chat_title: Optional[str] = None
    destination_chat_title: Optional[str] = None
    media_types: Optional[List[str]] = Field(None, description="Filter by media types")
    download_filter: Optional[str] = None
    limit: int = Field(0, description="Maximum messages to forward (0 = unlimited)")
    offset_id: int = Field(0, description="Start from message ID")
    forward_with_caption: bool = Field(True, description="Forward with captions")
    copy_media: bool = Field(False, description="Copy as new message instead of forward")
    account_id: Optional[int] = None


class ForwardTaskResponse(BaseModel):
    """Schema for forward task response"""
    id: int
    source_chat_id: str
    source_chat_title: str | None
    destination_chat_id: str
    destination_chat_title: str | None
    status: str
    total_count: int
    success_count: int
    failed_count: int
    skipped_count: int
    media_types: List[str] | None
    download_filter: str | None
    limit: int
    offset_id: int
    forward_with_caption: bool
    copy_media: bool
    account_id: int | None
    created_at: str | None
    started_at: str | None
    completed_at: str | None
    updated_at: str | None

    class Config:
        from_attributes = True
