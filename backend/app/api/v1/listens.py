"""
Listen API Routes - Real-time monitoring
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.listen import ListenSubscription
from app.schemas.listen import ListenSubscriptionCreate, ListenSubscriptionResponse
from app.services.listen_service import listen_service

router = APIRouter()


@router.get("/subscriptions", response_model=List[ListenSubscriptionResponse])
async def list_listen_subscriptions(
    db: AsyncSession = Depends(get_db),
):
    """List all listen subscriptions"""
    subscriptions = await listen_service.list_subscriptions(db)
    return [ListenSubscriptionResponse(**sub.to_dict()) for sub in subscriptions]


@router.post("/subscriptions", response_model=ListenSubscriptionResponse)
async def create_listen_subscription(
    data: ListenSubscriptionCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new listen subscription"""
    try:
        subscription = await listen_service.create_subscription(
            db=db,
            account_id=data.account_id,
            chat_id=data.chat_id,
            chat_title=data.chat_title,
            media_types=data.media_types,
            download_filter=data.download_filter,
            auto_forward=data.auto_forward,
            forward_to_chat_id=data.forward_to_chat_id,
        )
        return ListenSubscriptionResponse(**subscription.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/subscriptions/{subscription_id}/start")
async def start_listener(
    subscription_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Start listening for new messages"""
    try:
        await listen_service.start_listener(db, subscription_id)
        return {"message": "Listener started"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/subscriptions/{subscription_id}/stop")
async def stop_listener(
    subscription_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Stop a listener"""
    try:
        await listen_service.stop_listener(db, subscription_id)
        return {"message": "Listener stopped"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/subscriptions/{subscription_id}")
async def delete_listen_subscription(
    subscription_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete a listen subscription"""
    subscription = await db.get(ListenSubscription, subscription_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    # Stop listener if running
    if subscription.status.value == "active":
        await listen_service.stop_listener(db, subscription_id)

    await db.delete(subscription)
    await db.commit()

    return {"message": "Subscription deleted"}
