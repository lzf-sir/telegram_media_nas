"""
Application Configuration
"""
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field, validator
import os


class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "Telegram Media NAS"
    DEBUG: bool = False
    SECRET_KEY: str = Field(default="change-this-secret-key-in-production")

    # Database - SQLite (文件数据库)
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./data/telegram_media_nas.db"
    )

    # Redis
    REDIS_URL: str = Field(default="redis://redis:6379/0")

    # Paths
    DOWNLOAD_PATH: str = Field(default="./downloads")
    TEMP_PATH: str = Field(default="./temp")
    SESSION_PATH: str = Field(default="./sessions")

    # Telegram
    TELEGRAM_API_ID: int = Field(default=0)
    TELEGRAM_API_HASH: str = Field(default="")
    TELEGRAM_PHONE: str = Field(default="")

    # Telegram Bot（可选，用于 Bot 命令任务）
    TELEGRAM_BOT_TOKEN: str = Field(default="")

    # Celery
    CELERY_BROKER_URL: str = Field(default="redis://redis:6379/1")
    CELERY_RESULT_BACKEND: str = Field(default="redis://redis:6379/1")

    # CORS
    FRONTEND_ORIGINS: List[str] = Field(default=["http://localhost:5173", "http://localhost:3000"])

    # Download settings
    MAX_CONCURRENT_DOWNLOADS: int = Field(default=5)
    DOWNLOAD_TIMEOUT: int = Field(default=300)
    MAX_RETRIES: int = Field(default=3)

    # JWT
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60 * 24 * 7)  # 7 days

    @validator("FRONTEND_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @validator("DOWNLOAD_PATH", "TEMP_PATH", "SESSION_PATH", "pre=True)
    def create_paths(cls, v):
        path = os.path.abspath(v)
        os.makedirs(path, exist_ok=True)
        return path

    @validator("DATABASE_URL", pre=True)
    def create_db_path(cls, v):
        """确保 SQLite 数据库目录存在"""
        if v.startswith("sqlite+aiosqlite:///"):
            # 提取数据库文件路径
            db_path = v.replace("sqlite+aiosqlite:///", "")
            if db_path.startswith("./"):
                db_path = os.path.abspath(db_path)
            # 确保目录存在
            db_dir = os.path.dirname(db_path)
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
