from typing import Optional
from pydantic import BaseModel, EmailStr, validator
from datetime import datetime

from app.core.validators import (
    PASSWORD_MIN_LEN,
    USERNAME_MAX_LEN,
    USERNAME_MIN_LEN,
    normalize_email,
    normalize_username,
)

class UserBase(BaseModel):
    username: str
    email: EmailStr
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    is_active: Optional[bool] = True
    
    model_config={
        "from_attributes": True
    }

    @validator("username", pre=True)
    def _validate_username(cls, v: str) -> str:
        normalized = normalize_username(v)
        if not normalized:
            raise ValueError("Username is required")
        if not (USERNAME_MIN_LEN <= len(normalized) <= USERNAME_MAX_LEN):
            raise ValueError(f"Username length must be {USERNAME_MIN_LEN}-{USERNAME_MAX_LEN}")
        return normalized

    @validator("email", pre=True)
    def _validate_email(cls, v: str) -> str:
        normalized = normalize_email(v)
        if not normalized:
            raise ValueError("Email is required")
        return normalized

class UserCreate(UserBase):
    password: str

    @validator("password", pre=True)
    def _validate_password(cls, v: str) -> str:
        if v is None or not str(v).strip():
            raise ValueError("Password is required")
        if len(v) < PASSWORD_MIN_LEN:
            raise ValueError(f"Password length must be >= {PASSWORD_MIN_LEN}")
        return v

class UserUpdate(BaseModel):
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    is_active: Optional[bool] = None


class UserMeUpdate(BaseModel):
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

    @validator("current_password", pre=True)
    def _validate_current_password(cls, v: str) -> str:
        if v is None or not str(v).strip():
            raise ValueError("Current password is required")
        return str(v)

    @validator("new_password", pre=True)
    def _validate_new_password(cls, v: str) -> str:
        if v is None or not str(v).strip():
            raise ValueError("New password is required")
        if len(v) < PASSWORD_MIN_LEN:
            raise ValueError(f"Password length must be >= {PASSWORD_MIN_LEN}")
        return str(v)


class AvatarUploadResponse(BaseModel):
    avatar_url: str
 

# 返还给 前端的用户信息,一般只返回简单信息
class UserResponse(UserBase):
    id:int
    created_at: datetime
    updated_at:datetime
    is_superuser:bool
    


class UserOutWithFollowers(UserResponse):
    followers_count: int = 0
    following_count: int = 0
    

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
