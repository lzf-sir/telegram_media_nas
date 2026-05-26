"""
Tasks API Routes
"""
from typing import List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.task import DownloadTask, TaskStatus
from app.models.file import DownloadedFile
from app.schemas.task import (
    TaskCreate, TaskResponse, TaskUpdate,
    TaskDetailResponse, AvailableFormatsResponse,
    FileExtensionInfo, FILE_FORMATS_INFO
)
from app.services.task_service import task_service
from app.websocket.manager import manager

router = APIRouter()


@router.post("/", response_model=TaskResponse)
async def create_task(
    task_data: TaskCreate,
    db: AsyncSession = Depends(get_db),
):
    """创建新的下载任务"""
    task = await task_service.create_task(db, task_data)
    # Start the task asynchronously
    await task_service.start_task(task.id)
    return TaskResponse(**task.to_dict())


@router.get("/", response_model=List[TaskResponse])
async def list_tasks(
    status: Optional[str] = None,
    task_type: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """获取任务列表"""
    query = select(DownloadTask).order_by(desc(DownloadTask.created_at))

    if status:
        try:
            task_status = TaskStatus(status)
            query = query.where(DownloadTask.status == task_status)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")

    if task_type:
        from app.models.enums import TaskType
        try:
            TaskType(task_type)
            query = query.where(DownloadTask.task_type == task_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid task type: {task_type}")

    query = query.limit(limit).offset(offset)
    result = await db.execute(query)
    tasks = result.scalars().all()

    return [TaskResponse(**task.to_dict()) for task in tasks]


@router.get("/{task_id}", response_model=TaskDetailResponse)
async def get_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    获取任务详情
    包含文件列表和分类统计
    """
    result = await db.execute(select(DownloadTask).where(DownloadTask.id == task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # 获取任务文件
    files_result = await db.execute(
        select(DownloadedFile)
        .where(DownloadedFile.task_id == task_id)
        .order_by(desc(DownloadedFile.downloaded_at))
    )
    files = files_result.scalars().all()

    # 构建响应
    task_dict = task.to_dict()
    task_dict['files'] = [file.to_dict() for file in files]

    # 添加摘要信息
    task_dict['summary'] = {
        'total_files': len(files),
        'total_size': task.downloaded_bytes,
        'by_type': task.stats_by_type or {},
        'by_format': task.stats_by_format or {},
        'completion_rate': (task.success_count / task.total_count * 100) if task.total_count > 0 else 0
    }

    return TaskDetailResponse(**task_dict)


@router.get("/{task_id}/stats")
async def get_task_stats(
    task_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    获取任务统计信息
    按媒体类型和文件格式分类统计
    """
    result = await db.execute(select(DownloadTask).where(DownloadTask.id == task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # 获取文件统计
    stats_result = await db.execute(
        select(
            DownloadedFile.media_type,
            func.count(DownloadedFile.id).label('count'),
            func.sum(DownloadedFile.file_size).label('total_size')
        )
        .where(DownloadedFile.task_id == task_id)
        .group_by(DownloadedFile.media_type)
    )
    type_stats = stats_result.all()

    # 获取格式统计
    format_result = await db.execute(
        select(
            func.substr(DownloadedFile.file_name, func.instr(DownloadedFile.file_name, '.')).label('ext'),
            func.count(DownloadedFile.id).label('count')
        )
        .where(DownloadedFile.task_id == task_id)
        .group_by('ext')
        .order_by(desc('count'))
        .limit(20)
    )
    format_stats = format_result.all()

    return {
        'task_id': task_id,
        'status': task.status.value,
        'progress': {
            'total': task.total_count,
            'success': task.success_count,
            'failed': task.failed_count,
            'skipped': task.skipped_count,
            'bytes_downloaded': task.downloaded_bytes,
            'total_bytes': task.total_bytes,
        },
        'by_media_type': [
            {'type': stat.media_type, 'count': stat.count, 'total_size': stat.total_size or 0}
            for stat in type_stats
        ],
        'by_format': [
            {'extension': stat.ext or 'unknown', 'count': stat.count}
            for stat in format_stats
        ],
        'current_file': {
            'id': task.current_file_id,
            'name': task.current_file_name,
            'size': task.current_file_size,
            'progress': task.current_file_progress,
        } if task.current_file_id else None,
    }


@router.get("/formats/available", response_model=AvailableFormatsResponse)
async def get_available_formats():
    """
    获取所有可用的文件格式列表
    用于创建任务时选择过滤格式
    """
    # 按媒体类型分组
    by_type: Dict[str, List[FileExtensionInfo]] = {
        'photo': [],
        'video': [],
        'audio': [],
        'document': [],
        'voice': [],
        'animation': [],
    }

    for ext, info in FILE_FORMATS_INFO.items():
        media_type = info['media_type']
        by_type[media_type].append(FileExtensionInfo(
            extension=ext,
            name=info['name'],
            media_type=media_type,
            description=info['description']
        ))

    return AvailableFormatsResponse(
        by_media_type=by_type,
        all_extensions=list(FILE_FORMATS_INFO.keys())
    )


@router.delete("/{task_id}")
async def cancel_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
):
    """取消正在运行的任务"""
    result = await db.execute(select(DownloadTask).where(DownloadTask.id == task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.status not in [TaskStatus.PENDING, TaskStatus.RUNNING]:
        raise HTTPException(status_code=400, detail="Task cannot be cancelled")

    await task_service.cancel_task(task_id)

    return {"message": "Task cancelled"}


@router.post("/{task_id}/retry")
async def retry_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
):
    """重试任务中失败的下载"""
    result = await db.execute(select(DownloadTask).where(DownloadTask.id == task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.status == TaskStatus.RUNNING:
        raise HTTPException(status_code=400, detail="Task is currently running")

    new_task = await task_service.retry_failed(db, task_id)
    return TaskResponse(**new_task.to_dict())


@router.get("/{task_id}/files", response_model=List[dict])
async def get_task_files(
    task_id: int,
    media_type: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """
    获取任务的文件列表
    支持按媒体类型过滤
    """
    # Verify task exists
    result = await db.execute(select(DownloadTask).where(DownloadTask.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Get files
    query = (
        select(DownloadedFile)
        .where(DownloadedFile.task_id == task_id)
    )

    if media_type:
        query = query.where(DownloadedFile.media_type == media_type)

    query = query.order_by(desc(DownloadedFile.downloaded_at)).limit(limit).offset(offset)
    result = await db.execute(query)
    files = result.scalars().all()

    return [file.to_dict() for file in files]


@router.post("/{task_id}/pause")
async def pause_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    暂停正在运行的任务
    """
    result = await db.execute(select(DownloadTask).where(DownloadTask.id == task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.status != TaskStatus.RUNNING:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot pause task with status {task.status.value}"
        )

    await task_service.pause_task(task_id)
    return {"message": "Task paused"}


@router.post("/{task_id}/resume")
async def resume_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    恢复已暂停的任务
    """
    result = await db.execute(select(DownloadTask).where(DownloadTask.id == task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.status != TaskStatus.PAUSED:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot resume task with status {task.status.value}"
        )

    await task_service.resume_task(task_id)
    return {"message": "Task resumed"}
