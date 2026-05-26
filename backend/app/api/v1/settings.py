"""
Settings API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from loguru import logger

from app.core.config import settings
from app.database import AsyncSession, get_db
from app.models.system_setting import SystemSetting
from app.services.settings_service import SettingsService, settings_service
from app.core.security import get_current_active_user
from app.models.user import User

router = APIRouter()


# ==================== Schemas ====================

class TelegramSettings(BaseModel):
    """Telegram settings"""
    api_id: int
    api_hash: str
    phone: str


class DownloadSettings(BaseModel):
    """Download settings"""
    max_concurrent_downloads: int
    download_timeout: int
    download_path: str


class BotSettings(BaseModel):
    """Bot 安全设置"""
    rate_limit: int = Field(0, ge=0, le=1000, description="每分钟最大请求数，0表示不限制")
    whitelist_enabled: bool = Field(False, description="是否启用白名单")
    whitelist_users: list[str] = Field(default_factory=list, description="白名单用户列表")


# ==================== 现有端点 ====================

@router.get("/telegram")
async def get_telegram_settings():
    """Get Telegram settings"""
    return {
        "api_id": settings.TELEGRAM_API_ID,
        "api_hash": "***" if settings.TELEGRAM_API_HASH else "",
        "phone": settings.TELEGRAM_PHONE,
        "configured": bool(settings.TELEGRAM_API_ID and settings.TELEGRAM_API_HASH),
    }


@router.put("/telegram")
async def update_telegram_settings(settings_data: TelegramSettings):
    """Update Telegram settings (would save to database/env)"""
    # TODO: Implement proper settings persistence
    return {"message": "Settings updated"}


@router.get("/download")
async def get_download_settings():
    """Get download settings"""
    return {
        "max_concurrent_downloads": settings.MAX_CONCURRENT_DOWNLOADS,
        "download_timeout": settings.DOWNLOAD_TIMEOUT,
        "download_path": settings.DOWNLOAD_PATH,
    }


@router.put("/download")
async def update_download_settings(settings_data: DownloadSettings):
    """Update download settings"""
    # TODO: Implement proper settings persistence
    return {"message": "Settings updated"}


# ==================== 新增 Bot 设置端点 ====================

@router.get("/bot", response_model=BotSettings)
async def get_bot_settings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取 Bot 安全设置"""
    try:
        rate_limit = await SettingsService.get_int_setting(
            db, SettingsService.KEY_BOT_RATE_LIMIT, 0
        )
        whitelist_enabled = await SettingsService.get_bool_setting(
            db, SettingsService.KEY_BOT_WHITELIST_ENABLED, False
        )
        whitelist_users = await SettingsService.get_json_setting(
            db, SettingsService.KEY_BOT_WHITELIST_USERS, []
        )

        return BotSettings(
            rate_limit=rate_limit,
            whitelist_enabled=whitelist_enabled,
            whitelist_users=whitelist_users or []
        )
    except Exception as e:
        logger.error(f"获取 Bot 设置失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取设置失败"
        )


@router.put("/bot")
async def update_bot_settings(
    settings_data: BotSettings,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新 Bot 安全设置"""
    try:
        # 更新速率限制
        await SettingsService.set_int_setting(
            db, SettingsService.KEY_BOT_RATE_LIMIT, settings_data.rate_limit
        )

        # 更新白名单启用状态
        await SettingsService.set_bool_setting(
            db, SettingsService.KEY_BOT_WHITELIST_ENABLED, settings_data.whitelist_enabled
        )

        # 更新白名单用户列表
        await SettingsService.set_json_setting(
            db, SettingsService.KEY_BOT_WHITELIST_USERS, settings_data.whitelist_users
        )

        logger.info(f"Bot 设置已更新: rate_limit={settings_data.rate_limit}, "
                   f"whitelist_enabled={settings_data.whitelist_enabled}, "
                   f"whitelist_users={len(settings_data.whitelist_users)}")

        return {"message": "设置已更新"}
    except Exception as e:
        logger.error(f"更新 Bot 设置失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新设置失败"
        )


# ==================== 通用设置端点 ====================

@router.get("/all")
async def get_all_settings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取所有设置"""
    try:
        all_settings = await SettingsService.get_all_settings(db)
        return all_settings
    except Exception as e:
        logger.error(f"获取所有设置失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取设置失败"
        )


@router.get("/{key}")
async def get_setting(
    key: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取单个设置值"""
    result = await db.execute(
        select(SystemSetting).where(SystemSetting.key == key)
    )
    setting = result.scalar_one_or_none()

    if setting is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"设置 {key} 不存在"
        )

    return {
        "key": setting.key,
        "value": setting.value,
        "value_type": setting.value_type
    }


@router.put("/{key}")
async def update_setting(
    key: str,
    value: str,
    value_type: str = "string",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新单个设置值"""
    try:
        setting = await SettingsService.set_setting(db, key, value, value_type)
        return {
            "message": "设置已更新",
            "setting": setting.to_dict()
        }
    except Exception as e:
        logger.error(f"更新设置失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新设置失败"
        )
