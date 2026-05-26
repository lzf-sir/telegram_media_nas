"""
用户相关的 Pydantic schemas
"""
from pydantic import BaseModel, Field, validator


class InitSystemRequest(BaseModel):
    """系统初始化请求"""
    username: str = Field(..., min_length=3, max_length=50, description="管理员用户名")
    password: str = Field(..., min_length=6, max_length=100, description="密码")
    password_confirm: str = Field(..., description="确认密码")

    @validator("password_confirm")
    def passwords_match(cls, v, values):
        """验证两次密码是否一致"""
        if "password" in values and v != values["password"]:
            raise ValueError("两次输入的密码不一致")
        return v

    @validator("username")
    def username_alphanumeric(cls, v):
        """用户名只能包含字母、数字和下划线"""
        if not v.replace("_", "").isalnum():
            raise ValueError("用户名只能包含字母、数字和下划线")
        return v


class LoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class UserResponse(BaseModel):
    """用户响应"""
    id: int
    username: str
    is_admin: bool

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Token 响应"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class InitStatusResponse(BaseModel):
    """初始化状态响应"""
    initialized: bool
