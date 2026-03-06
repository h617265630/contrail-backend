from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.deps import get_db_dep, get_current_user, PermissionChecker
from app.models.rbac.user import User
from app.schemas.rbac.permission import PermissionCreate, PermissionUpdate, PermissionResponse
from app.curd.rbac.permission_curd import PermissionCURD

router = APIRouter(prefix="/permission", tags=["Permission"])

# 权限管理
@router.get("/permissions", response_model=List[PermissionResponse])
async def get_permissions(
    db: Session = Depends(get_db_dep),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    module: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """获取权限列表（需要权限：permission.read）"""
    if module:
        return PermissionCURD.get_permissions_by_module(db, module)
    return PermissionCURD.get_permissions(db, skip=skip, limit=limit)

@router.get("/permissions/{permission_id}", response_model=PermissionResponse)
async def get_permission(
    permission_id: int,
    db: Session = Depends(get_db_dep),
    current_user: User = Depends(PermissionChecker(["permission.read"]))
):
    """获取权限详情"""
    permission = PermissionCURD.get_permission_by_id(db, permission_id)
    if not permission:
        raise HTTPException(status_code=404, detail="权限不存在")
    return permission

@router.post("/permissions", response_model=PermissionResponse, status_code=status.HTTP_201_CREATED)
async def create_permission(
    permission_in: PermissionCreate,
    db: Session = Depends(get_db_dep),
    current_user: User = Depends(PermissionChecker(["permission.create"]))
):
    """创建权限"""
    # 检查权限代码是否已存在
    existing = PermissionCURD.get_permission_by_code(db, permission_in.code)
    if existing:
        raise HTTPException(status_code=400, detail="权限代码已存在")
    
    return PermissionCURD.create_permission(db, permission_in)

@router.put("/permissions/{permission_id}", response_model=PermissionResponse)
async def update_permission(
    permission_id: int,
    permission_update: PermissionUpdate,
    db: Session = Depends(get_db_dep),
    current_user: User = Depends(PermissionChecker(["permission.update"]))
):
    """更新权限"""
    permission = PermissionCURD.update_permission(db, permission_id, permission_update.dict(exclude_unset=True))
    if not permission:
        raise HTTPException(status_code=404, detail="权限不存在")
    return permission

@router.delete("/permissions/{permission_id}")
async def delete_permission(
    permission_id: int,
    db: Session = Depends(get_db_dep),
    current_user: User = Depends(PermissionChecker(["permission.delete"]))
):
    """删除权限"""
    success = PermissionCURD.delete_permission(db, permission_id)
    if not success:
        raise HTTPException(status_code=404, detail="权限不存在")
    return {"message": "权限删除成功"}