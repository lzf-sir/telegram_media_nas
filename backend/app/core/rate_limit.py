"""
速率限制模块 - 基于 slowapi 实现
"""
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from loguru import logger

from app.database import AsyncSession, get_db
from app.services.settings_service import SettingsService


# 创建速率限制器
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200/hour"],  # 默认每小时 200 次请求
    storage_uri="memory://",  # 使用内存存储
)


async def get_bot_rate_limit(request: Request) -> str:
    """
    获取 Bot 速率限制配置

    从数据库读取配置的速率限制值
    返回格式："{次数}/{时间单位}"

    Returns:
        速率限制字符串，如 "10/minute" 或 "0/minute"（不限制）
    """
    try:
        # 从 request.state 获取 db（需要在依赖中注入）
        db: AsyncSession = getattr(request.state, "db", None)
        if db is None:
            # 如果没有 db，使用默认值
            return "60/minute"

        rate_limit = await SettingsService.get_int_setting(
            db, SettingsService.KEY_BOT_RATE_LIMIT, 0
        )

        if rate_limit <= 0:
            # 0 表示不限制，设置一个很高的值
            return "1000/minute"

        return f"{rate_limit}/minute"

    except Exception as e:
        logger.error(f"获取速率限制配置失败: {e}")
        return "60/minute"  # 默认值


def get_default_rate_limit() -> str:
    """
    获取默认的速率限制

    Returns:
        速率限制字符串
    """
    return "60/minute"


# 自定义速率限制异常处理
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """
    速率限制异常处理器
    """
    logger.warning(f"速率限制触发: {request.client.host}")
    from fastapi import JSONResponse
    return JSONResponse(
        status_code=429,
        content={
            "detail": f"请求过于频繁，请稍后再试。限制：{exc.detail}"
        },
    )
