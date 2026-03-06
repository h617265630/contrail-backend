# 用户角色管理
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.deps import get_db_dep, PermissionChecker
from app.models.rbac.user import User
from app.schemas.rbac.user_role import UserRoleAssign, UserWithRoles
from app.curd.rbac.role_curd import RoleCURD
from app.curd.rbac.user_curd import UserCURD

router = APIRouter(prefix="/user-role", tags=["UserRole"])

@router.get("/users/{user_id}/roles", response_model=UserWithRoles)
async def get_user_roles(
    user_id: int,
    db: Session = Depends(get_db_dep),
    current_user: User = Depends(PermissionChecker(["user.role.read"]))
):
    """获取用户的角色"""
    user = UserCURD.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user

@router.post("/users/{user_id}/roles")
async def assign_user_roles(
    user_id: int,
    assign_data: UserRoleAssign,
    db: Session = Depends(get_db_dep),
    current_user: User = Depends(PermissionChecker(["user.role.assign"]))
):
    """为用户分配角色"""
    user = UserCURD.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 获取要分配的角色
    roles = []
    for role_id in assign_data.role_ids:
        role = RoleCURD.get_role_by_id(db, role_id)
        if not role:
            raise HTTPException(status_code=404, detail=f"角色 {role_id} 不存在")
        if not role.is_active:
            raise HTTPException(status_code=400, detail=f"角色 {role.name} 已被禁用")
        roles.append(role)
    
    # 检查权限等级：不能为用户分配比自己等级低的角色
    if not current_user.is_superuser:
        current_user_level = min([role.level for role in current_user.roles], default=1000)
        for role in roles:
            if role.level < current_user_level:
                raise HTTPException(
                    status_code=403,
                    detail=f"不能分配等级高于自己的角色: {role.name}"
                )
    
    # 分配角色
    user.roles = roles
    db.commit()
    db.refresh(user)
    
    return {"message": "角色分配成功", "roles": [role.to_dict() for role in user.roles]}


