# 权限检查
from fastapi import APIRouter, Depends
from app.core.deps import  get_current_user
from app.models.rbac import User
from app.schemas.rbac import (
   PermissionCheck
)

router = APIRouter(prefix="/role-permission", tags=["RolePermission"])

@router.post("/check-permission")
async def check_permission(
    check: PermissionCheck,
    current_user: User = Depends(get_current_user)
):
    """检查当前用户是否有指定权限"""
    has_permission = current_user.has_permission(check.permission_code) or current_user.is_superuser
    return {
        "has_permission": has_permission,
        "permission": check.permission_code,
        "is_superuser": current_user.is_superuser
    }

@router.get("/my-permissions")
async def get_my_permissions(
    current_user: User = Depends(get_current_user)
):
    """获取当前用户的所有权限"""
    return {
        "permissions": current_user.get_all_permissions(),
        "roles": [role.code for role in current_user.roles],
        "is_superuser": current_user.is_superuser
    }