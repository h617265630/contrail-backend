# backend/app/routers/rbac.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.core.deps import get_db_dep, get_current_user, PermissionChecker
from app.models.rbac.user import User
from app.schemas.rbac.role import (
    RoleCreate, RoleUpdate, RoleResponse,
)
from app.schemas.rbac.permission import PermissionCheck,PermissionResponse

from app.curd.rbac.role_curd import RoleCURD

router = APIRouter(prefix="/role", tags=["Role"])

# 角色管理
@router.get("/roles", response_model=List[RoleResponse])
async def get_roles(
    db: Session = Depends(get_db_dep),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = Query(False),
    current_user: User = Depends(get_current_user)
):
    """获取角色列表（需要权限：role.read）"""
    if active_only:
        return RoleCURD.get_active_roles(db)
    return RoleCURD.get_roles(db, skip=skip, limit=limit)

@router.get("/roles/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: int,
    db: Session = Depends(get_db_dep),
    current_user: User = Depends(PermissionChecker(["role.read"]))
):
    """获取角色详情"""
    role = RoleCURD.get_role_by_id(db, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    return role

@router.post("/roles", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    role_in: RoleCreate,
    db: Session = Depends(get_db_dep),
    current_user: User = Depends(PermissionChecker(["role.create"]))
):
    """创建角色"""
    # 检查角色代码是否已存在
    existing = RoleCURD.get_role_by_code(db, role_in.code)
    if existing:
        raise HTTPException(status_code=400, detail="角色代码已存在")
    
    return RoleCURD.create_role(db, role_in)

@router.put("/roles/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: int,
    role_update: RoleUpdate,
    db: Session = Depends(get_db_dep),
    current_user: User = Depends(PermissionChecker(["role.update"]))
):
    """更新角色"""
    # 不能修改系统角色
    role = RoleCURD.get_role_by_id(db, role_id)
    if role and role.is_system:
        raise HTTPException(status_code=400, detail="不能修改系统角色")
    
    update_data = role_update.dict(exclude_unset=True)
    
    # 如果更新了权限
    if "permission_ids" in update_data:
        permissions = update_data.pop("permission_ids")
        RoleCURD.assign_permissions(db, role_id, permissions)
    
    if update_data:
        role = RoleCURD.update_role(db, role_id, update_data)
    
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    return role

@router.delete("/roles/{role_id}")
async def delete_role(
    role_id: int,
    db: Session = Depends(get_db_dep),
    current_user: User = Depends(PermissionChecker(["role.delete"]))
):
    """删除角色"""
    success = RoleCURD.delete_role(db, role_id)
    if not success:
        raise HTTPException(status_code=404, detail="角色不存在或为系统角色")
    return {"message": "角色删除成功"}



# 权限检查
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