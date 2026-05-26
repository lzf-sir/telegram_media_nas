"""
Telegram Media NAS - Main Application Entry
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.api.v1 import auth, tasks, files, chats, settings as settings_api, accounts, forwards, listens, logs
from app.core.config import settings
from app.database import init_db, close_db
from app.websocket.manager import websocket_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting Telegram Media NAS...")
    await init_db()

    # 清理临时文件并恢复未完成的任务
    try:
        from app.services.task_service import task_service
        await task_service.recover_running_tasks()
    except Exception as e:
        logger.error(f"Failed to recover tasks: {e}")

    yield
    logger.info("Shutting down Telegram Media NAS...")
    await close_db()


app = FastAPI(
    title="Telegram Media NAS",
    description="Telegram media download and management system",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["Tasks"])
app.include_router(files.router, prefix="/api/v1/files", tags=["Files"])
app.include_router(chats.router, prefix="/api/v1/chats", tags=["Chats"])
app.include_router(settings_api.router, prefix="/api/v1/settings", tags=["Settings"])
app.include_router(accounts.router, prefix="/api/v1/accounts", tags=["Accounts"])
app.include_router(forwards.router, prefix="/api/v1/forwards", tags=["Forwards"])
app.include_router(listens.router, prefix="/api/v1/listens", tags=["Listens"])
app.include_router(logs.router, prefix="/api/v1/logs", tags=["Logs"])

# WebSocket router
app.include_router(websocket_router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Telegram Media NAS",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}
