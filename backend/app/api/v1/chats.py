"""
Chats API Routes
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.chat import ChatSubscription
from app.schemas.chat import ChatSubscribe, ChatResponse, ChatUpdate
from app.core.telegram import telegram_manager

router = APIRouter()


@router.get("/dialogs")
async def list_dialogs(
    limit: int = Query(50, ge=1, le=100),
):
    """Get list of Telegram dialogs (chats)"""
    try:
        dialogs = await telegram_manager.get_dialogs(limit=limit)
        return [
            {
                "id": str(dialog.chat.id),
                "title": dialog.chat.title or dialog.chat.first_name or dialog.chat.username,
                "username": dialog.chat.username,
                "type": dialog.chat.type.value,
                "photo_url": None,  # Could add photo URL extraction
            }
            for dialog in dialogs
        ]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dialogs: {str(e)}")


@router.get("/subscriptions", response_model=List[ChatResponse])
async def list_subscriptions(
    db: AsyncSession = Depends(get_db),
):
    """List all chat subscriptions"""
    result = await db.execute(
        select(ChatSubscription).order_by(desc(ChatSubscription.created_at))
    )
    subscriptions = result.scalars().all()

    return [ChatResponse(**sub.to_dict()) for sub in subscriptions]


@router.post("/subscribe", response_model=ChatResponse)
async def subscribe_chat(
    chat_data: ChatSubscribe,
    db: AsyncSession = Depends(get_db),
):
    """Subscribe to a chat for downloading"""
    # Check if already exists
    existing = await db.execute(
        select(ChatSubscription).where(ChatSubscription.chat_id == chat_data.chat_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Already subscribed to this chat")

    subscription = ChatSubscription(
        chat_id=chat_data.chat_id,
        chat_title=chat_data.chat_title,
        chat_username=chat_data.chat_username,
        chat_type=chat_data.chat_type,
        media_types=chat_data.media_types,
        download_filter=chat_data.download_filter,
        auto_download=chat_data.auto_download,
    )

    db.add(subscription)
    await db.commit()
    await db.refresh(subscription)

    return ChatResponse(**subscription.to_dict())


@router.get("/subscriptions/{chat_id}", response_model=ChatResponse)
async def get_subscription(
    chat_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get chat subscription details"""
    result = await db.execute(
        select(ChatSubscription).where(ChatSubscription.chat_id == chat_id)
    )
    subscription = result.scalar_one_or_none()

    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    return ChatResponse(**subscription.to_dict())


@router.put("/subscriptions/{chat_id}", response_model=ChatResponse)
async def update_subscription(
    chat_id: str,
    update_data: ChatUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update chat subscription"""
    result = await db.execute(
        select(ChatSubscription).where(ChatSubscription.chat_id == chat_id)
    )
    subscription = result.scalar_one_or_none()

    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    # Update fields
    if update_data.is_active is not None:
        subscription.is_active = update_data.is_active
    if update_data.media_types is not None:
        subscription.media_types = update_data.media_types
    if update_data.download_filter is not None:
        subscription.download_filter = update_data.download_filter
    if update_data.auto_download is not None:
        subscription.auto_download = update_data.auto_download

    await db.commit()
    await db.refresh(subscription)

    return ChatResponse(**subscription.to_dict())


@router.delete("/subscriptions/{chat_id}")
async def unsubscribe_chat(
    chat_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Unsubscribe from a chat"""
    result = await db.execute(
        select(ChatSubscription).where(ChatSubscription.chat_id == chat_id)
    )
    subscription = result.scalar_one_or_none()

    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    await db.delete(subscription)
    await db.commit()

    return {"message": "Unsubscribed successfully"}
