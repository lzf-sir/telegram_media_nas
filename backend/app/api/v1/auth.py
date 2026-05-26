"""
认证 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from loguru import logger

from app.database import AsyncSession, get_db
from app.models.user import User
from app.models.system_setting import SystemSetting
from app.schemas.user import (
    InitSystemRequest,
    LoginRequest,
    TokenResponse,
    UserResponse,
    InitStatusResponse,
)
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_active_user,
)

router = APIRouter()

# 系统初始化标记的 key
INITIALIZED_KEY = "system_initialized"


@router.get("/init-status", response_model=InitStatusResponse)
async def get_init_status(db: AsyncSession = Depends(get_db)):
    """
    检查系统是否已初始化
    """
    result = await db.execute(
        select(SystemSetting).where(SystemSetting.key == INITIALIZED_KEY)
    )
    setting = result.scalar_one_or_none()

    initialized = setting is not None and setting.value == "true"

    return InitStatusResponse(initialized=initialized)


@router.post("/init", response_model=TokenResponse)
async def initialize_system(
    data: InitSystemRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    初始化系统，创建管理员账户
    只能在系统未初始化时调用
    """
    # 检查是否已初始化
    result = await db.execute(
        select(SystemSetting).where(SystemSetting.key == INITIALIZED_KEY)
    )
    setting = result.scalar_one_or_none()

    if setting and setting.value == "true":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="系统已经初始化，请直接登录",
        )

    # 检查用户名是否已存在
    result = await db.execute(select(User).where(User.username == data.username))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在",
        )

    # 创建管理员用户
    user = User(
        username=data.username,
        password_hash=get_password_hash(data.password),
        is_admin=True,
    )
    db.add(user)

    # 创建系统初始化标记
    init_setting = SystemSetting(key=INITIALIZED_KEY, value="true")
    db.add(init_setting)

    await db.commit()
    await db.refresh(user)

    logger.info(f"系统初始化完成，管理员用户: {data.username}")

    # 生成 token
    access_token = create_access_token(data={"sub": user.id})

    return TokenResponse(
        access_token=access_token,
        user=UserResponse(id=user.id, username=user.username, is_admin=user.is_admin),
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    用户登录
    """
    # 查找用户
    result = await db.execute(select(User).where(User.username == credentials.username))
    user = result.scalar_one_or_none()

    # 验证用户和密码
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 生成 token
    access_token = create_access_token(data={"sub": user.id})

    logger.info(f"用户登录成功: {user.username}")

    return TokenResponse(
        access_token=access_token,
        user=UserResponse(id=user.id, username=user.username, is_admin=user.is_admin),
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    current_user: User = Depends(get_current_active_user),
):
    """
    获取当前登录用户信息
    """
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        is_admin=current_user.is_admin,
    )


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_active_user)):
    """
    退出登录（客户端需要删除 token）
    """
    logger.info(f"用户退出登录: {current_user.username}")
    return {"message": "退出登录成功"}
