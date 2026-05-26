"""
Logs API Routes
"""
from typing import List, Optional
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, desc, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.log import ActivityLog, LogLevel, LogType

router = APIRouter()


@router.get("/")
async def list_logs(
    level: Optional[str] = None,
    log_type: Optional[str] = None,
    task_id: Optional[int] = None,
    chat_id: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """List activity logs with filtering"""
    query = select(ActivityLog)

    # Build filters
    conditions = []
    if level:
        try:
            log_level = LogLevel(level)
            conditions.append(ActivityLog.level == log_level)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid log level: {level}")

    if log_type:
        try:
            log_t = LogType(log_type)
            conditions.append(ActivityLog.log_type == log_t)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid log type: {log_type}")

    if task_id:
        conditions.append(ActivityLog.task_id == task_id)

    if chat_id:
        conditions.append(ActivityLog.chat_id == chat_id)

    if conditions:
        query = query.where(and_(*conditions))

    # Get total count
    from sqlalchemy import func
    count_query = select(func.count()).select_from(ActivityLog)
    if conditions:
        count_query = count_query.where(and_(*conditions))
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Get paginated results
    query = query.order_by(desc(ActivityLog.created_at))
    query = query.limit(limit).offset(offset)
    result = await db.execute(query)
    logs = result.scalars().all()

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "logs": [log.to_dict() for log in logs],
    }


@router.get("/stats")
async def get_log_stats(
    db: AsyncSession = Depends(get_db),
):
    """Get log statistics"""
    from sqlalchemy import func

    # Count by level
    level_stats = await db.execute(
        select(ActivityLog.level, func.count(ActivityLog.id))
        .group_by(ActivityLog.level)
    )
    by_level = {row.level.value: row.count for row in level_stats}

    # Count by type
    type_stats = await db.execute(
        select(ActivityLog.log_type, func.count(ActivityLog.id))
        .group_by(ActivityLog.log_type)
    )
    by_type = {row.log_type.value: row.count for row in type_stats}

    # Recent errors
    recent_errors = await db.execute(
        select(ActivityLog)
        .where(ActivityLog.level == LogLevel.ERROR)
        .order_by(desc(ActivityLog.created_at))
        .limit(10)
    )
    errors = [log.to_dict() for log in recent_errors.scalars().all()]

    return {
        "by_level": by_level,
        "by_type": by_type,
        "recent_errors": errors,
    }


@router.delete("/old")
async def delete_old_logs(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
):
    """Delete logs older than specified days"""
    from app.models.log import ActivityLog

    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)

    result = await db.execute(
        select(ActivityLog).where(ActivityLog.created_at < cutoff_date)
    )
    logs_to_delete = result.scalars().all()

    count = len(logs_to_delete)
    for log in logs_to_delete:
        await db.delete(log)

    await db.commit()

    return {"message": f"Deleted {count} old logs"}
