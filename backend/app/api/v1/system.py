"""
系统健康检查 API
"""
import shutil
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.task import DownloadTask, TaskStatus
from app.models.file import DownloadedFile
from app.models.account import TelegramAccount
from app.models.listen import ListenSubscription, ListenStatus
from app.core.config import settings

router = APIRouter()


@router.get("/health")
async def get_system_health(
    db: AsyncSession = Depends(get_db),
):
    """获取系统健康状态和资源使用情况"""

    # 磁盘使用情况
    disk_info = {}
    for path_key, path in [
        ("downloads", settings.DOWNLOAD_PATH),
        ("temp", settings.TEMP_PATH),
    ]:
        try:
            usage = shutil.disk_usage(path)
            disk_info[path_key] = {
                "path": path,
                "total_gb": round(usage.total / (1024 ** 3), 2),
                "used_gb": round(usage.used / (1024 ** 3), 2),
                "free_gb": round(usage.free / (1024 ** 3), 2),
                "used_percent": round(usage.used / usage.total * 100, 1),
                "status": "warning" if usage.free / usage.total < 0.1 else "ok",
            }
        except Exception:
            disk_info[path_key] = {"path": path, "status": "unavailable"}

    # 任务队列状态
    running_count = await db.scalar(
        select(func.count(DownloadTask.id)).where(
            DownloadTask.status.in_([TaskStatus.RUNNING, TaskStatus.PENDING])
        )
    )
    paused_count = await db.scalar(
        select(func.count(DownloadTask.id)).where(DownloadTask.status == TaskStatus.PAUSED)
    )
    completed_today = await db.scalar(
        select(func.count(DownloadTask.id)).where(DownloadTask.status == TaskStatus.COMPLETED)
    )

    # 活跃监听数
    active_listens = await db.scalar(
        select(func.count(ListenSubscription.id)).where(
            ListenSubscription.status == ListenStatus.ACTIVE
        )
    )

    # 活跃账号数
    active_accounts = await db.scalar(
        select(func.count(TelegramAccount.id)).where(TelegramAccount.status == "active")
    )

    # 总文件统计
    total_files = await db.scalar(select(func.count(DownloadedFile.id)))
    total_storage = await db.scalar(select(func.sum(DownloadedFile.file_size)))

    return {
        "status": "healthy",
        "disk": disk_info,
        "queue": {
            "running": running_count or 0,
            "paused": paused_count or 0,
            "max_concurrent": settings.MAX_CONCURRENT_DOWNLOADS,
            "concurrent_percent": round(
                (running_count or 0) / settings.MAX_CONCURRENT_DOWNLOADS * 100, 1
            ) if settings.MAX_CONCURRENT_DOWNLOADS > 0 else 0,
        },
        "listeners": {
            "active": active_listens or 0,
        },
        "accounts": {
            "active": active_accounts or 0,
        },
        "storage": {
            "total_files": total_files or 0,
            "total_bytes": total_storage or 0,
        },
        "completed_today": completed_today or 0,
    }
