"""
Files API Routes
"""
import os
import mimetypes
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse, Response
from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.file import DownloadedFile
from app.schemas.file import FileResponse, FileListResponse, FileStats

router = APIRouter()


@router.get("/", response_model=FileListResponse)
async def list_files(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    chat_id: Optional[str] = None,
    media_type: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """List downloaded files with pagination and filtering"""
    # Build query
    query = select(DownloadedFile)

    # Apply filters
    conditions = []
    if chat_id:
        conditions.append(DownloadedFile.chat_id == chat_id)
    if media_type:
        conditions.append(DownloadedFile.media_type == media_type)
    if search:
        search_pattern = f"%{search}%"
        conditions.append(
            or_(
                DownloadedFile.file_name.ilike(search_pattern),
                DownloadedFile.caption.ilike(search_pattern),
            )
        )

    if conditions:
        query = query.where(and_(*conditions))

    # Get total count
    count_query = select(func.count()).select_from(DownloadedFile)
    if conditions:
        count_query = count_query.where(and_(*conditions))
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Get paginated results
    query = query.order_by(desc(DownloadedFile.downloaded_at))
    query = query.limit(page_size).offset((page - 1) * page_size)
    result = await db.execute(query)
    files = result.scalars().all()

    return FileListResponse(
        total=total,
        page=page,
        page_size=page_size,
        files=[FileResponse(**file.to_dict()) for file in files],
    )


@router.get("/stats", response_model=FileStats)
async def get_file_stats(
    db: AsyncSession = Depends(get_db),
):
    """Get file statistics"""
    # Total files and size
    total_result = await db.execute(
        select(
            func.count(DownloadedFile.id).label("count"),
            func.sum(DownloadedFile.file_size).label("size"),
        )
    )
    total_row = total_result.one()
    total_files = total_row.count or 0
    total_size = total_row.size or 0

    # By media type
    media_type_result = await db.execute(
        select(
            DownloadedFile.media_type,
            func.count(DownloadedFile.id).label("count"),
            func.sum(DownloadedFile.file_size).label("size"),
        ).group_by(DownloadedFile.media_type)
    )
    by_media_type = {
        row.media_type: {"count": row.count, "size": row.size}
        for row in media_type_result
    }

    # By chat
    chat_result = await db.execute(
        select(
            DownloadedFile.chat_id,
            func.count(DownloadedFile.id).label("count"),
            func.sum(DownloadedFile.file_size).label("size"),
        )
        .group_by(DownloadedFile.chat_id)
        .order_by(desc(func.count(DownloadedFile.id)))
        .limit(10)
    )
    by_chat = {
        row.chat_id: {"count": row.count, "size": row.size}
        for row in chat_result
    }

    return FileStats(
        total_files=total_files,
        total_size=total_size,
        by_media_type=by_media_type,
        by_chat=by_chat,
    )


@router.get("/{file_id}", response_model=FileResponse)
async def get_file(
    file_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get file details"""
    result = await db.execute(select(DownloadedFile).where(DownloadedFile.id == file_id))
    file = result.scalar_one_or_none()

    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(**file.to_dict())


@router.delete("/{file_id}")
async def delete_file(
    file_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete a file record and the actual file"""
    result = await db.execute(select(DownloadedFile).where(DownloadedFile.id == file_id))
    file = result.scalar_one_or_none()

    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    # Delete actual file
    import os
    if os.path.exists(file.file_path):
        try:
            os.remove(file.file_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")

    # Delete thumbnail if exists
    if file.thumbnail_path and os.path.exists(file.thumbnail_path):
        try:
            os.remove(file.thumbnail_path)
        except Exception:
            pass

    # Delete database record
    await db.delete(file)
    await db.commit()

    return {"message": "File deleted"}


@router.delete("/batch")
async def delete_files_batch(
    file_ids: List[int],
    db: AsyncSession = Depends(get_db),
):
    """Delete multiple files"""
    result = await db.execute(
        select(DownloadedFile).where(DownloadedFile.id.in_(file_ids))
    )
    files = result.scalars().all()

    deleted_count = 0
    errors = []

    for file in files:
        import os
        if os.path.exists(file.file_path):
            try:
                os.remove(file.file_path)
                if file.thumbnail_path and os.path.exists(file.thumbnail_path):
                    os.remove(file.thumbnail_path)
                await db.delete(file)
                deleted_count += 1
            except Exception as e:
                errors.append(f"{file.file_name}: {str(e)}")

    await db.commit()

    return {
        "deleted_count": deleted_count,
        "errors": errors,
    }


@router.get("/{file_id}/preview")
async def preview_file(
    file_id: int,
    db: AsyncSession = Depends(get_db),
):
    """预览文件（图片直接显示，视频返回信息）"""
    result = await db.execute(select(DownloadedFile).where(DownloadedFile.id == file_id))
    file = result.scalar_one_or_none()

    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    if not os.path.exists(file.file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")

    # 图片类型直接返回文件
    if file.media_type == "photo" or (file.mime_type and file.mime_type.startswith("image/")):
        mime_type, _ = mimetypes.guess_type(file.file_path)
        return FileResponse(
            file.file_path,
            media_type=mime_type or "image/jpeg",
            filename=file.file_name,
        )

    # 非图片返回信息
    return {
        "id": file.id,
        "file_name": file.file_name,
        "media_type": file.media_type,
        "mime_type": file.mime_type,
        "file_size": file.file_size,
        "preview_available": False,
    }


@router.get("/{file_id}/thumbnail")
async def get_thumbnail(
    file_id: int,
    db: AsyncSession = Depends(get_db),
):
    """获取文件缩略图（图片直接返回，其他返回 204）"""
    result = await db.execute(select(DownloadedFile).where(DownloadedFile.id == file_id))
    file = result.scalar_one_or_none()

    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    if not os.path.exists(file.file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")

    # 图片类型直接返回文件作为缩略图
    if file.media_type == "photo" or (file.mime_type and file.mime_type.startswith("image/")):
        mime_type, _ = mimetypes.guess_type(file.file_path)
        return FileResponse(file.file_path, media_type=mime_type or "image/jpeg")

    # 非图片返回 204（前端显示图标）
    return Response(status_code=204)
