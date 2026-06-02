"""
Database Connection and Session Management
使用 SQLite 数据库 (aiosqlite 驱动)
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from loguru import logger

from app.core.config import settings

# SQLite 不支持连接池配置，使用基本配置
# SQLite 在同一时间只允许一个写操作
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
)

# Create async session maker
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Base class for models
Base = declarative_base()


async def get_db() -> AsyncSession:
    """Dependency for getting async database session"""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize database - create tables"""
    async with engine.begin() as conn:
        # 导入所有模型以确保它们在 Base.metadata 中注册
        from app.models import task, file, chat, user, system_setting, account, forward, listen, log, filter  # noqa
        await conn.run_sync(Base.metadata.create_all)
    logger.info("数据库初始化完成")


async def close_db():
    """Close database connection"""
    await engine.dispose()
    logger.info("Database connection closed")
