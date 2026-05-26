"""
File Schemas
"""
from typing import Optional, List
from pydantic import BaseModel, Field


class FileResponse(BaseModel):
    """Schema for file response"""
    id: int
    task_id: int
    message_id: int
    chat_id: str
    file_name: Optional[str]
    file_path: str
    file_size: int
    file_unique_id: Optional[str]
    mime_type: Optional[str]
    media_type: str
    duration: Optional[int]
    width: Optional[int]
    height: Optional[int]
    caption: Optional[str]
    thumbnail_path: Optional[str]
    md5_hash: str
    downloaded_at: Optional[str]

    class Config:
        from_attributes = True


class FileListResponse(BaseModel):
    """Schema for file list response"""
    total: int
    page: int
    page_size: int
    files: List[FileResponse]


class FileStats(BaseModel):
    """Schema for file statistics"""
    total_files: int
    total_size: int
    by_media_type: dict
    by_chat: dict
