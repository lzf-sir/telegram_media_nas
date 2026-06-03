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
    """下载设置"""
    max_concurrent_downloads: int = 5
    download_timeout: int = 300
    download_path: str = "./downloads"
    temp_path: str = "./temp"


class BotSettings(BaseModel):
    """Bot 安全设置"""
    rate_limit: int = Field(0, ge=0, le=1000, description="每分钟最大请求数，0表示不限制")
    whitelist_enabled: bool = Field(False, description="是否启用白名单")
    whitelist_users: list[str] = Field(default_factory=list, description="白名单用户列表")


# ==================== 现有端点 ====================

@router.get("/telegram")
async def get_telegram_settings(
    db: AsyncSession = Depends(get_db),
):
    """获取 Telegram 设置（优先读取数据库覆盖值，回退到环境变量）"""
    # 尝试从数据库读取覆盖值
    db_api_id = await settings_service.get_setting(db, "telegram_api_id")
    db_api_hash = await settings_service.get_setting(db, "telegram_api_hash")
    db_phone = await settings_service.get_setting(db, "telegram_phone")

    api_id = int(db_api_id) if db_api_id else settings.TELEGRAM_API_ID
    api_hash = db_api_hash or settings.TELEGRAM_API_HASH
    phone = db_phone or settings.TELEGRAM_PHONE

    return {
        "api_id": api_id,
        "api_hash": "***" if api_hash else "",
        "phone": phone,
        "configured": bool(api_id and api_hash),
    }


@router.put("/telegram")
async def update_telegram_settings(
    settings_data: TelegramSettings,
    db: AsyncSession = Depends(get_db),
):
    """更新 Telegram 设置（持久化到数据库）"""
    try:
        await settings_service.set_setting(db, "telegram_api_id", str(settings_data.api_id), "int")
        await settings_service.set_setting(db, "telegram_api_hash", settings_data.api_hash)
        await settings_service.set_setting(db, "telegram_phone", settings_data.phone)

        # 同时更新运行时配置
        settings.TELEGRAM_API_ID = settings_data.api_id
        settings.TELEGRAM_API_HASH = settings_data.api_hash
        settings.TELEGRAM_PHONE = settings_data.phone

        logger.info("Telegram 设置已更新并持久化")
        return {"message": "Settings updated", "configured": bool(settings_data.api_id and settings_data.api_hash)}
    except Exception as e:
        logger.error(f"更新 Telegram 设置失败: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/telegram/test")
async def test_telegram_connection(
    db: AsyncSession = Depends(get_db),
):
    """测试 Telegram 连接"""
    try:
        db_api_id = await settings_service.get_setting(db, "telegram_api_id")
        db_api_hash = await settings_service.get_setting(db, "telegram_api_hash")
        db_phone = await settings_service.get_setting(db, "telegram_phone")

        api_id = int(db_api_id) if db_api_id else settings.TELEGRAM_API_ID
        api_hash = db_api_hash or settings.TELEGRAM_API_HASH
        phone = db_phone or settings.TELEGRAM_PHONE

        if not (api_id and api_hash):
            raise HTTPException(status_code=400, detail="Telegram 未配置")

        from app.core.telegram import telegram_manager
        client = await telegram_manager.get_client(api_id, api_hash, phone, "test_session")
        me = await client.get_me()
        return {"status": "ok", "message": f"已连接到 {me.first_name} (@{me.username or 'N/A'})"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Telegram 连接测试失败: {e}")
        raise HTTPException(status_code=500, detail=f"连接测试失败: {str(e)}")


@router.get("/download")
async def get_download_settings(
    db: AsyncSession = Depends(get_db),
):
    """获取下载设置（优先读取数据库覆盖值）"""
    db_max_concurrent = await settings_service.get_setting(db, "max_concurrent_downloads")
    db_timeout = await settings_service.get_setting(db, "download_timeout")
    db_path = await settings_service.get_setting(db, "download_path")
    db_temp_path = await settings_service.get_setting(db, "temp_path")

    return {
        "max_concurrent_downloads": int(db_max_concurrent) if db_max_concurrent else settings.MAX_CONCURRENT_DOWNLOADS,
        "download_timeout": int(db_timeout) if db_timeout else settings.DOWNLOAD_TIMEOUT,
        "download_path": db_path or settings.DOWNLOAD_PATH,
        "temp_path": db_temp_path or settings.TEMP_PATH,
    }


@router.put("/download")
async def update_download_settings(
    settings_data: DownloadSettings,
    db: AsyncSession = Depends(get_db),
):
    """更新下载设置（持久化到数据库）"""
    try:
        await settings_service.set_setting(db, "max_concurrent_downloads", str(settings_data.max_concurrent_downloads), "int")
        await settings_service.set_setting(db, "download_timeout", str(settings_data.download_timeout), "int")
        await settings_service.set_setting(db, "download_path", settings_data.download_path)
        await settings_service.set_setting(db, "temp_path", settings_data.temp_path)

        # 同时更新运行时配置
        settings.MAX_CONCURRENT_DOWNLOADS = settings_data.max_concurrent_downloads
        settings.DOWNLOAD_TIMEOUT = settings_data.download_timeout
        settings.DOWNLOAD_PATH = settings_data.download_path
        settings.TEMP_PATH = settings_data.temp_path

        logger.info("下载设置已更新并持久化")
        return {"message": "Settings updated"}
    except Exception as e:
        logger.error(f"更新下载设置失败: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


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
    """获取所有设置（包含 Telegram、下载和数据库设置）"""
    try:
        # 获取数据库中的通用设置
        db_settings = await SettingsService.get_all_settings(db)

        # 获取 Telegram 设置
        db_api_id = await settings_service.get_setting(db, "telegram_api_id")
        db_api_hash = await settings_service.get_setting(db, "telegram_api_hash")
        db_phone = await settings_service.get_setting(db, "telegram_phone")

        telegram_settings = {
            "api_id": int(db_api_id) if db_api_id else settings.TELEGRAM_API_ID,
            "api_hash": "***" if (db_api_hash or settings.TELEGRAM_API_HASH) else "",
            "phone": db_phone or settings.TELEGRAM_PHONE,
            "configured": bool((db_api_id or settings.TELEGRAM_API_ID) and (db_api_hash or settings.TELEGRAM_API_HASH)),
        }

        # 获取下载设置
        db_max_concurrent = await settings_service.get_setting(db, "max_concurrent_downloads")
        db_timeout = await settings_service.get_setting(db, "download_timeout")
        db_path = await settings_service.get_setting(db, "download_path")
        db_temp_path = await settings_service.get_setting(db, "temp_path")

        download_settings = {
            "max_concurrent_downloads": int(db_max_concurrent) if db_max_concurrent else settings.MAX_CONCURRENT_DOWNLOADS,
            "download_timeout": int(db_timeout) if db_timeout else settings.DOWNLOAD_TIMEOUT,
            "download_path": db_path or settings.DOWNLOAD_PATH,
            "temp_path": db_temp_path or settings.TEMP_PATH,
        }

        return {
            "telegram": telegram_settings,
            "download": download_settings,
            "settings": db_settings,
        }
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
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新单个设置值"""
    try:
        value = data.get("value", "")
        value_type = data.get("value_type", "string")
        setting = await SettingsService.set_setting(db, key, str(value), value_type)
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
