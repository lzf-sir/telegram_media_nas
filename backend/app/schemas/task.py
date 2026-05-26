"""
Task Schemas
"""
from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    """创建下载任务的 Schema"""
    chat_id: str = Field(..., description="要下载的聊天 ID")
    chat_title: Optional[str] = Field(None, description="聊天标题")
    task_type: str = Field(
        default="onetime",
        description="任务类型: bot(Bot命令任务) 或 onetime(一次性下载任务)"
    )
    media_types: Optional[List[str]] = Field(
        default=None,
        description="要下载的媒体类型: audio, video, photo, document, voice, video_note, animation"
    )
    download_filter: Optional[str] = Field(None, description="下载过滤表达式")
    # 文件格式过滤
    excluded_extensions: Optional[List[str]] = Field(
        default_factory=list,
        description="排除的文件扩展名列表，如: ['.exe', '.tmp']"
    )
    included_extensions: Optional[List[str]] = Field(
        default_factory=list,
        description="包含的文件扩展名列表（优先级高于排除），为空则接受所有格式"
    )
    limit: Optional[int] = Field(0, description="最大处理消息数量，0 表示无限制")
    offset_id: Optional[int] = Field(0, description="起始消息 ID")


class TaskResponse(BaseModel):
    """任务响应 Schema"""
    id: int
    chat_id: str
    chat_title: Optional[str]
    task_type: str
    status: str
    total_count: int
    success_count: int
    failed_count: int
    skipped_count: int
    downloaded_bytes: int
    total_bytes: int
    stats_by_type: Dict[str, int]
    stats_by_format: Dict[str, int]
    current_file_id: Optional[int]
    current_file_name: Optional[str]
    current_file_size: Optional[int]
    current_file_progress: float
    media_types: Optional[List[str]]
    download_filter: Optional[str]
    excluded_extensions: Optional[List[str]]
    included_extensions: Optional[List[str]]
    limit: int
    offset_id: int
    created_at: Optional[str]
    started_at: Optional[str]
    completed_at: Optional[str]
    updated_at: Optional[str]
    progress: Optional[float] = None  # 计算的进度百分比

    class Config:
        from_attributes = True


class TaskUpdate(BaseModel):
    """更新任务的 Schema"""
    status: Optional[str] = None


class TaskProgress(BaseModel):
    """任务进度更新 Schema"""
    task_id: int
    status: str
    total_count: int
    success_count: int
    failed_count: int
    skipped_count: int
    downloaded_bytes: int
    total_bytes: int
    current_file: Optional[str] = None
    current_file_progress: float = 0.0
    speed: Optional[float] = None  # bytes per second
    eta: Optional[int] = None  # estimated time in seconds


class TaskDetailResponse(TaskResponse):
    """任务详情响应 - 包含文件列表和统计"""
    files: List[Dict] = Field(default_factory=list)
    summary: Optional[Dict] = None


class FileExtensionInfo(BaseModel):
    """文件扩展名信息"""
    extension: str
    name: str
    media_type: str
    description: str


class AvailableFormatsResponse(BaseModel):
    """可用文件格式响应"""
    by_media_type: Dict[str, List[FileExtensionInfo]]
    all_extensions: List[str]


# 预定义的文件格式信息
FILE_FORMATS_INFO = {
    # 图片
    ".jpg": {"name": "JPEG 图片", "media_type": "photo", "description": "常见的图片格式"},
    ".jpeg": {"name": "JPEG 图片", "media_type": "photo", "description": "常见的图片格式"},
    ".png": {"name": "PNG 图片", "media_type": "photo", "description": "支持透明度的图片格式"},
    ".gif": {"name": "GIF 动图", "media_type": "photo", "description": "支持动画的图片格式"},
    ".webp": {"name": "WebP 图片", "media_type": "photo", "description": "Google 开发的高效图片格式"},
    ".bmp": {"name": "BMP 图片", "media_type": "photo", "description": "位图格式"},
    ".tiff": {"name": "TIFF 图片", "media_type": "photo", "description": "高质量图片格式"},
    ".svg": {"name": "SVG 矢量图", "media_type": "photo", "description": "可缩放矢量图形"},
    ".ico": {"name": "ICO 图标", "media_type": "photo", "description": "图标文件格式"},

    # 视频
    ".mp4": {"name": "MP4 视频", "media_type": "video", "description": "最通用的视频格式"},
    ".avi": {"name": "AVI 视频", "media_type": "video", "description": "经典视频格式"},
    ".mkv": {"name": "MKV 视频", "media_type": "video", "description": "高质量视频容器"},
    ".mov": {"name": "MOV 视频", "media_type": "video", "description": "QuickTime 视频格式"},
    ".wmv": {"name": "WMV 视频", "media_type": "video", "description": "Windows 媒体视频"},
    ".flv": {"name": "FLV 视频", "media_type": "video", "description": "Flash 视频格式"},
    ".webm": {"name": "WebM 视频", "media_type": "video", "description": "Web 优化视频格式"},
    ".m4v": {"name": "M4V 视频", "media_type": "video", "description": "iTunes 视频格式"},
    ".ts": {"name": "TS 视频", "media_type": "video", "description": "传输流视频格式"},
    ".rmvb": {"name": "RMVB 视频", "media_type": "video", "description": "RealMedia 变比特率格式"},

    # 音频
    ".mp3": {"name": "MP3 音频", "media_type": "audio", "description": "最通用的音频格式"},
    ".flac": {"name": "FLAC 音频", "media_type": "audio", "description": "无损压缩音频"},
    ".aac": {"name": "AAC 音频", "media_type": "audio", "description": "高效压缩音频"},
    ".ogg": {"name": "OGG 音频", "media_type": "audio", "description": "开源音频格式"},
    ".wav": {"name": "WAV 音频", "media_type": "audio", "description": "无损波形音频"},
    ".m4a": {"name": "M4A 音频", "media_type": "audio", "description": "AAC 音频容器"},
    ".wma": {"name": "WMA 音频", "media_type": "audio", "description": "Windows 媒体音频"},
    ".opus": {"name": "Opus 音频", "media_type": "audio", "description": "高效音频编解码"},
    ".ape": {"name": "APE 音频", "media_type": "audio", "description": "无损音频格式"},

    # 文档
    ".pdf": {"name": "PDF 文档", "media_type": "document", "description": "便携式文档格式"},
    ".doc": {"name": "Word 文档", "media_type": "document", "description": "旧版 Word 格式"},
    ".docx": {"name": "Word 文档", "media_type": "document", "description": "新版 Word 格式"},
    ".xls": {"name": "Excel 表格", "media_type": "document", "description": "旧版 Excel 格式"},
    ".xlsx": {"name": "Excel 表格", "media_type": "document", "description": "新版 Excel 格式"},
    ".ppt": {"name": "PowerPoint 演示", "media_type": "document", "description": "旧版 PowerPoint 格式"},
    ".pptx": {"name": "PowerPoint 演示", "media_type": "document", "description": "新版 PowerPoint 格式"},
    ".txt": {"name": "文本文件", "media_type": "document", "description": "纯文本文件"},
    ".rtf": {"name": "RTF 文档", "media_type": "document", "description": "富文本格式"},
    ".csv": {"name": "CSV 表格", "media_type": "document", "description": "逗号分隔值文件"},
    ".epub": {"name": "EPUB 电子书", "media_type": "document", "description": "电子书格式"},
    ".mobi": {"name": "MOBI 电子书", "media_type": "document", "description": "Kindle 电子书格式"},

    # 压缩文件
    ".zip": {"name": "ZIP 压缩", "media_type": "document", "description": "通用压缩格式"},
    ".rar": {"name": "RAR 压缩", "media_type": "document", "description": "RAR 压缩格式"},
    ".7z": {"name": "7Z 压缩", "media_type": "document", "description": "7-Zip 压缩格式"},
    ".tar": {"name": "TAR 归档", "media_type": "document", "description": "TAR 归档格式"},
    ".gz": {"name": "GZ 压缩", "media_type": "document", "description": "Gzip 压缩格式"},

    # 可执行文件
    ".exe": {"name": "EXE 可执行", "media_type": "document", "description": "Windows 可执行文件"},
    ".apk": {"name": "APK 安装包", "media_type": "document", "description": "Android 安装包"},
    ".dmg": {"name": "DMG 镜像", "media_type": "document", "description": "macOS 磁盘镜像"},
    ".iso": {"name": "ISO 镜像", "media_type": "document", "description": "光盘镜像文件"},
}
