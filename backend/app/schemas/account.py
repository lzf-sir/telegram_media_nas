"""
Account Schemas
"""
from pydantic import BaseModel, Field


class AccountCreate(BaseModel):
    """Schema for creating a Telegram account"""
    phone: str = Field(..., description="Phone number with country code, e.g., +1234567890")
    api_id: int = Field(..., description="Telegram API ID")
    api_hash: str = Field(..., description="Telegram API Hash")
    session_name: str = Field(None, description="Custom session name (optional)")
    is_default: bool = Field(False, description="Set as default account")


class AccountResponse(BaseModel):
    """Schema for account response"""
    id: int
    phone: str
    api_id: int
    api_hash: str
    user_id: int | None
    username: str | None
    first_name: str | None
    last_name: str | None
    status: str
    is_default: bool
    session_name: str
    last_used_at: str | None
    last_error: str | None
    created_at: str | None
    updated_at: str | None

    class Config:
        from_attributes = True
