"""
Forward API Routes
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.forward import ForwardTask
from app.schemas.forward import ForwardTaskCreate, ForwardTaskResponse
from app.services.forward_service import forward_service

router = APIRouter()


@router.get("/", response_model=List[ForwardTaskResponse])
async def list_forward_tasks(
    db: AsyncSession = Depends(get_db),
):
    """List all forward tasks"""
    tasks = await forward_service.list_tasks(db)
    return [ForwardTaskResponse(**task.to_dict()) for task in tasks]


@router.post("/", response_model=ForwardTaskResponse)
async def create_forward_task(
    data: ForwardTaskCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new forward task"""
    try:
        task = await forward_service.create_task(
            db=db,
            source_chat_id=data.source_chat_id,
            destination_chat_id=data.destination_chat_id,
            source_chat_title=data.source_chat_title,
            destination_chat_title=data.destination_chat_title,
            media_types=data.media_types,
            download_filter=data.download_filter,
            limit=data.limit,
            offset_id=data.offset_id,
            forward_with_caption=data.forward_with_caption,
            copy_media=data.copy_media,
            account_id=data.account_id,
        )

        # Start the task
        await forward_service.start_task(db, task.id)

        return ForwardTaskResponse(**task.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{task_id}/cancel")
async def cancel_forward_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Cancel a forward task"""
    try:
        await forward_service.cancel_task(db, task_id)
        return {"message": "Task cancelled"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{task_id}", response_model=ForwardTaskResponse)
async def get_forward_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get forward task details"""
    task = await db.get(ForwardTask, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return ForwardTaskResponse(**task.to_dict())
