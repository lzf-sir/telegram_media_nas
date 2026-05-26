"""
系统设置服务 - 管理系统级配置
"""
import json
from typing import Any, Optional, List
from sqlalchemy import select
from loguru import logger

from app.database import AsyncSession
from app.models.system_setting import SystemSetting


class SettingsService:
    """系统设置服务"""

    # 设置键名常量
    KEY_BOT_RATE_LIMIT = "bot_rate_limit"
    KEY_BOT_WHITELIST_ENABLED = "bot_whitelist_enabled"
    KEY_BOT_WHITELIST_USERS = "bot_whitelist_users"
    KEY_SYSTEM_INITIALIZED = "system_initialized"

    # 默认值
    DEFAULTS = {
        KEY_BOT_RATE_LIMIT: "0",  # 0 表示不限制
        KEY_BOT_WHITELIST_ENABLED: "false",
        KEY_BOT_WHITELIST_USERS: "[]",
    }

    @staticmethod
    async def get_setting(
        db: AsyncSession,
        key: str,
        default: Optional[str] = None
    ) -> Optional[str]:
        """
        获取单个设置值

        Args:
            db: 数据库会话
            key: 设置键名
            default: 默认值

        Returns:
            设置值或默认值
        """
        result = await db.execute(
            select(SystemSetting).where(SystemSetting.key == key)
        )
        setting = result.scalar_one_or_none()

        if setting is None:
            return default
        return setting.value

    @staticmethod
    async def set_setting(
        db: AsyncSession,
        key: str,
        value: str,
        value_type: str = "string"
    ) -> SystemSetting:
        """
        设置单个值

        Args:
            db: 数据库会话
            key: 设置键名
            value: 设置值
            value_type: 值类型

        Returns:
            设置对象
        """
        result = await db.execute(
            select(SystemSetting).where(SystemSetting.key == key)
        )
        setting = result.scalar_one_or_none()

        if setting:
            setting.value = value
            setting.value_type = value_type
        else:
            setting = SystemSetting(key=key, value=value, value_type=value_type)
            db.add(setting)

        await db.commit()
        await db.refresh(setting)

        logger.info(f"设置更新: {key} = {value}")
        return setting

    @staticmethod
    async def get_json_setting(
        db: AsyncSession,
        key: str,
        default: Optional[Any] = None
    ) -> Any:
        """
        获取 JSON 类型的设置值

        Args:
            db: 数据库会话
            key: 设置键名
            default: 默认值

        Returns:
            解析后的 JSON 对象或默认值
        """
        value_str = await SettingsService.get_setting(db, key)
        if value_str is None:
            return default

        try:
            return json.loads(value_str)
        except json.JSONDecodeError:
            logger.warning(f"JSON 解析失败: {key} = {value_str}")
            return default

    @staticmethod
    async def set_json_setting(
        db: AsyncSession,
        key: str,
        value: Any
    ) -> SystemSetting:
        """
        设置 JSON 类型的值

        Args:
            db: 数据库会话
            key: 设置键名
            value: 要设置的值（会被序列化为 JSON）

        Returns:
            设置对象
        """
        value_str = json.dumps(value, ensure_ascii=False)
        return await SettingsService.set_setting(db, key, value_str, "json")

    @staticmethod
    async def get_bool_setting(
        db: AsyncSession,
        key: str,
        default: bool = False
    ) -> bool:
        """
        获取布尔类型的设置值

        Args:
            db: 数据库会话
            key: 设置键名
            default: 默认值

        Returns:
            布尔值
        """
        value_str = await SettingsService.get_setting(db, key)
        if value_str is None:
            return default
        return value_str.lower() in ("true", "1", "yes", "on")

    @staticmethod
    async def set_bool_setting(
        db: AsyncSession,
        key: str,
        value: bool
    ) -> SystemSetting:
        """
        设置布尔类型的值

        Args:
            db: 数据库会话
            key: 设置键名
            value: 布尔值

        Returns:
            设置对象
        """
        value_str = "true" if value else "false"
        return await SettingsService.set_setting(db, key, value_str, "bool")

    @staticmethod
    async def get_int_setting(
        db: AsyncSession,
        key: str,
        default: int = 0
    ) -> int:
        """
        获取整数类型的设置值

        Args:
            db: 数据库会话
            key: 设置键名
            default: 默认值

        Returns:
            整数值
        """
        value_str = await SettingsService.get_setting(db, key)
        if value_str is None:
            return default

        try:
            return int(value_str)
        except ValueError:
            logger.warning(f"整数解析失败: {key} = {value_str}")
            return default

    @staticmethod
    async def set_int_setting(
        db: AsyncSession,
        key: str,
        value: int
    ) -> SystemSetting:
        """
        设置整数类型的值

        Args:
            db: 数据库会话
            key: 设置键名
            value: 整数值

        Returns:
            设置对象
        """
        value_str = str(value)
        return await SettingsService.set_setting(db, key, value_str, "int")

    @staticmethod
    async def get_all_settings(db: AsyncSession) -> dict[str, Any]:
        """
        获取所有设置

        Args:
            db: 数据库会话

        Returns:
            所有设置的字典
        """
        result = await db.execute(select(SystemSetting))
        settings = result.scalars().all()

        settings_dict = {}
        for setting in settings:
            # 根据类型解析值
            if setting.value_type == "json":
                try:
                    settings_dict[setting.key] = json.loads(setting.value)
                except json.JSONDecodeError:
                    settings_dict[setting.key] = setting.value
            elif setting.value_type == "bool":
                settings_dict[setting.key] = setting.value.lower() in ("true", "1", "yes")
            elif setting.value_type == "int":
                try:
                    settings_dict[setting.key] = int(setting.value)
                except ValueError:
                    settings_dict[setting.key] = setting.value
            else:
                settings_dict[setting.key] = setting.value

        return settings_dict

    @staticmethod
    async def is_user_in_whitelist(
        db: AsyncSession,
        user_id: int,
        username: Optional[str] = None
    ) -> bool:
        """
        检查用户是否在白名单中

        Args:
            db: 数据库会话
            user_id: Telegram 用户 ID
            username: Telegram 用户名（可选）

        Returns:
            是否在白名单中
        """
        # 如果白名单未启用，允许所有用户
        whitelist_enabled = await SettingsService.get_bool_setting(
            db, SettingsService.KEY_BOT_WHITELIST_ENABLED, False
        )
        if not whitelist_enabled:
            return True

        # 获取白名单用户
        whitelist_users = await SettingsService.get_json_setting(
            db, SettingsService.KEY_BOT_WHITELIST_USERS, []
        )

        if not whitelist_users:
            return True  # 白名单为空，允许所有用户

        # 检查用户 ID
        user_id_str = str(user_id)
        if user_id_str in whitelist_users:
            return True

        # 检查用户名
        if username:
            username_with_at = f"@{username}" if not username.startswith("@") else username
            username_without_at = username.lstrip("@")
            if username_with_at in whitelist_users or username_without_at in whitelist_users:
                return True

        return False


# 全局服务实例
settings_service = SettingsService()
