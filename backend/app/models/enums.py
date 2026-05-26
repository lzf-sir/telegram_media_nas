"""
项目通用枚举定义
包含任务类型、文件格式等枚举
import enum
from typing import List, Dict


class TaskType(str, enum.Enum):
    """任务类型枚举"""
    # Bot 任务：通过 Telegram Bot 下发命令下载或转发
    BOT = "bot"
    # 一次性任务：通过 chat_id 一次性下载聊天/频道所有媒体
    ONETIME = "onetime"


class FileExtension(str, enum.Enum):
    """文件扩展名枚举 - 用于格式过滤

    按媒体类型分类的常见文件格式
    """
    # 图片格式
    JPG = ".jpg"
    JPEG = ".jpeg"
    PNG = ".png"
    GIF = ".gif"
    WEBP = ".webp"
    BMP = ".bmp"
    TIFF = ".tiff"
    SVG = ".svg"
    ICO = ".ico"

    # 视频格式
    MP4 = ".mp4"
    AVI = ".avi"
    MKV = ".mkv"
    MOV = ".mov"
    WMV = ".wmv"
    FLV = ".flv"
    WEBM = ".webm"
    M4V = ".m4v"
    TS = ".ts"
    RMVB = ".rmvb"

    # 音频格式
    MP3 = ".mp3"
    FLAC = ".flac"
    AAC = ".aac"
    OGG = ".ogg"
    WAV = ".wav"
    M4A = ".m4a"
    WMA = ".wma"
    OPUS = ".opus"
    APE = ".ape"

    # 文档格式
    PDF = ".pdf"
    DOC = ".doc"
    DOCX = ".docx"
    XLS = ".xls"
    XLSX = ".xlsx"
    PPT = ".ppt"
    PPTX = ".pptx"
    TXT = ".txt"
    RTF = ".rtf"
    ODT = ".odt"
    ODS = ".ods"
    ODP = ".odp"
    CSV = ".csv"
    EPUB = ".epub"
    MOBI = ".mobi"

    # 压缩格式
    ZIP = ".zip"
    RAR = ".rar"
    SEVENZ = ".7z"
    TAR = ".tar"
    GZ = ".gz"
    BZ2 = ".bz2"
    XZ = ".xz"

    # 其他格式
    EXE = ".exe"
    APK = ".apk"
    DLL = ".dll"
    SO = ".so"
    BIN = ".bin"
    DMG = ".dmg"
    ISO = ".iso"

    @classmethod
    def get_by_media_type(cls, media_type: str) -> List[str]:
        """根据媒体类型获取相关文件扩展名

        Args:
            media_type: 媒体类型 (audio, video, photo, document, voice, animation)

        Returns:
            该媒体类型对应的扩展名列表
        """
        mapping = {
            "audio": [
                cls.MP3, cls.FLAC, cls.AAC, cls.OGG,
                cls.WAV, cls.M4A, cls.WMA, cls.OPUS, cls.APE
            ],
            "video": [
                cls.MP4, cls.AVI, cls.MKV, cls.MOV,
                cls.WMV, cls.FLV, cls.WEBM, cls.M4V, cls.TS, cls.RMVB
            ],
            "photo": [
                cls.JPG, cls.JPEG, cls.PNG, cls.GIF,
                cls.WEBP, cls.BMP, cls.TIFF, cls.SVG, cls.ICO
            ],
            "document": [
                cls.PDF, cls.DOC, cls.DOCX, cls.XLS, cls.XLSX,
                cls.PPT, cls.PPTX, cls.TXT, cls.RTF, cls.ODT,
                cls.ODS, cls.ODP, cls.CSV, cls.EPUB, cls.MOBI,
                # 压缩文件也归为文档
                cls.ZIP, cls.RAR, cls.SEVENZ, cls.TAR, cls.GZ,
                cls.BZ2, cls.XZ
            ],
            "voice": [cls.OGG, cls.OPUS, cls.WAV],
            "animation": [cls.GIF, cls.WEBM, cls.MP4],
        }
        return [ext.value for ext in mapping.get(media_type, [])]

    @classmethod
    def all_extensions(cls) -> List[str]:
        """获取所有支持的扩展名"""
        return [ext.value for ext in cls]

    @classmethod
    def from_string(cls, value: str) -> 'FileExtension':
        """从字符串转换为枚举值（自动添加点号）"""
        if not value.startswith('.'):
            value = '.' + value
        try:
            return cls(value.lower())
        except ValueError:
            # 如果不是预定义的扩展名，返回一个通用的
            return cls.BIN
