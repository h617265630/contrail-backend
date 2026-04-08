# app/deps.py
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.db.database import get_db
from app import auth
from app.curd.rbac.user_curd import UserCURD
from app.core.config import settings
from app.models.rbac.user import User
from typing import List, Optional, Sequence

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

def get_db_dep():
    yield from get_db()

def get_current_user_optional(db: Session = Depends(get_db_dep), request: Request = None) -> Optional[User]:
    """Optional auth: returns None if no valid token, instead of raising exception."""
    # Extract token from Authorization header manually
    auth_header = None
    if request:
        auth_header = request.headers.get("Authorization", "")

    if not auth_header:
        return None

    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None

    token = parts[1]
    if not token:
        return None

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            return None
    except Exception:
        return None

    user = UserCURD.get_user(db, int(user_id))
    return user

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db_dep)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception()
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise credentials_exception()

    user = UserCURD.get_user(db, int(user_id))
    if user is None:
        raise credentials_exception()
    return user

def get_current_active_user(current_user = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def credentials_exception():
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


# 权限检查依赖

class PermissionChecker:
    def __init__(self, required_permissions: Sequence[str]):
        self.required_permissions = list(required_permissions)

    def __call__(self, current_user: User = Depends(get_current_user)):
        # 超级管理员拥有所有权限
        if current_user.is_superuser:
            return current_user
        
        # 检查用户是否拥有所有必需权限
        user_permissions = current_user.get_all_permissions()
        
        for permission in self.required_permissions:
            if permission not in user_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"权限不足，需要权限: {permission}"
                )
        
        return current_user
    

# 角色检查依赖
class RoleChecker:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles
    
    def __call__(self, current_user: User = Depends(get_current_user)):
        # 超级管理员拥有所有角色
        if current_user.is_superuser:
            return current_user
        
        # 检查用户是否有任一允许的角色
        user_roles = {role.code for role in current_user.roles}
        
        for role in self.allowed_roles:
            if role in user_roles:
                return current_user
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"权限不足，需要角色: {', '.join(self.allowed_roles)}"
        )
    
# 检查单个权限的依赖
def has_permission(permission_code: str):
    def permission_dependency(current_user: User = Depends(get_current_user)):
        if not current_user.has_permission(permission_code) and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"权限不足，需要权限: {permission_code}"
            )
        return current_user
    return permission_dependency

# 检查单个角色的依赖
def has_role(role_code: str):
    def role_dependency(current_user: User = Depends(get_current_user)):
        if not current_user.has_role(role_code) and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"权限不足，需要角色: {role_code}"
            )
        return current_user
    return role_dependency