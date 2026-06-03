"""
收藏聊天 API
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database import get_db
from app.models.favorite import FavoriteChat

router = APIRouter()


class FavoriteCreate(BaseModel):
    chat_id: str
    chat_title: str = None
    note: str = None


class FavoriteResponse(BaseModel):
    id: int
    chat_id: str
    chat_title: str | None
    note: str | None
    created_at: str | None


@router.get("/", response_model=List[FavoriteResponse])
async def list_favorites(db: AsyncSession = Depends(get_db)):
    """获取所有收藏"""
    result = await db.execute(select(FavoriteChat).order_by(FavoriteChat.created_at.desc()))
    return [FavoriteResponse(**f.to_dict()) for f in result.scalars().all()]


@router.post("/", response_model=FavoriteResponse)
async def create_favorite(data: FavoriteCreate, db: AsyncSession = Depends(get_db)):
    """添加收藏"""
    existing = await db.execute(
        select(FavoriteChat).where(FavoriteChat.chat_id == data.chat_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="该聊天已在收藏中")

    fav = FavoriteChat(chat_id=data.chat_id, chat_title=data.chat_title, note=data.note)
    db.add(fav)
    await db.commit()
    await db.refresh(fav)
    return FavoriteResponse(**fav.to_dict())


@router.delete("/{fav_id}")
async def delete_favorite(fav_id: int, db: AsyncSession = Depends(get_db)):
    """删除收藏"""
    fav = await db.get(FavoriteChat, fav_id)
    if not fav:
        raise HTTPException(status_code=404, detail="未找到")
    await db.delete(fav)
    await db.commit()
    return {"message": "已删除"}


@router.delete("/by-chat/{chat_id}")
async def delete_favorite_by_chat(chat_id: str, db: AsyncSession = Depends(get_db)):
    """按 chat_id 删除收藏"""
    result = await db.execute(
        select(FavoriteChat).where(FavoriteChat.chat_id == chat_id)
    )
    fav = result.scalar_one_or_none()
    if fav:
        await db.delete(fav)
        await db.commit()
    return {"message": "已删除"}
