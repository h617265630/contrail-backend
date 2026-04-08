from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional

from app.core.deps import get_db_dep, get_current_user, PermissionChecker
from app.models.rbac.user import User
from app.schemas.admin import (
    AdminStatsResponse,
    AdminUserListResponse,
    AdminLearningPathListResponse,
    AdminResourceListResponse,
    AdminAnalyticsResponse,
)
from app.curd.admin_curd import AdminCURD

router = APIRouter(prefix="/admin", tags=["Admin"])


def require_superuser(current_user: User = Depends(get_current_user)):
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


@router.get("/stats", response_model=AdminStatsResponse)
async def get_admin_stats(
    db: Session = Depends(get_db_dep),
    current_user: User = Depends(require_superuser),
):
    """Get dashboard statistics - superuser only"""
    return AdminCURD.get_stats(db)


@router.get("/users", response_model=AdminUserListResponse)
async def get_admin_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    is_superuser: Optional[bool] = None,
    db: Session = Depends(get_db_dep),
    current_user: User = Depends(PermissionChecker(["user.read"])),
):
    """Get paginated user list with filters"""
    users, total = AdminCURD.get_users(
        db, skip=skip, limit=limit, search=search, is_active=is_active, is_superuser=is_superuser
    )
    return AdminUserListResponse(users=users, total=total, skip=skip, limit=limit)


@router.patch("/users/{user_id}/toggle-status")
async def toggle_user_status(
    user_id: int,
    db: Session = Depends(get_db_dep),
    current_user: User = Depends(PermissionChecker(["user.update"])),
):
    """Toggle user active status"""
    user = AdminCURD.toggle_user_status(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User status updated", "is_active": user.is_active}


@router.patch("/users/{user_id}/toggle-superuser")
async def toggle_superuser_status(
    user_id: int,
    db: Session = Depends(get_db_dep),
    current_user: User = Depends(require_superuser),
):
    """Toggle user superuser status - superuser only"""
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="Cannot modify your own superuser status")
    user = AdminCURD.toggle_superuser_status(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User superuser status updated", "is_superuser": user.is_superuser}


@router.get("/learning-paths", response_model=AdminLearningPathListResponse)
async def get_admin_learning_paths(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db_dep),
    current_user: User = Depends(require_superuser),
):
    """Get all learning paths for admin"""
    paths, total = AdminCURD.get_learning_paths(db, skip=skip, limit=limit)
    return AdminLearningPathListResponse(paths=paths, total=total)


@router.delete("/learning-paths/{path_id}")
async def delete_learning_path(
    path_id: int,
    db: Session = Depends(get_db_dep),
    current_user: User = Depends(require_superuser),
):
    """Delete a learning path - superuser only"""
    success = AdminCURD.delete_learning_path(db, path_id)
    if not success:
        raise HTTPException(status_code=404, detail="Learning path not found")
    return {"message": "Learning path deleted"}


@router.get("/resources", response_model=AdminResourceListResponse)
async def get_admin_resources(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db_dep),
    current_user: User = Depends(require_superuser),
):
    """Get all resources for admin"""
    resources, total = AdminCURD.get_resources(db, skip=skip, limit=limit)
    return AdminResourceListResponse(resources=resources, total=total)


@router.delete("/resources/{resource_id}")
async def delete_resource(
    resource_id: int,
    db: Session = Depends(get_db_dep),
    current_user: User = Depends(require_superuser),
):
    """Delete a resource - superuser only"""
    success = AdminCURD.delete_resource(db, resource_id)
    if not success:
        raise HTTPException(status_code=404, detail="Resource not found")
    return {"message": "Resource deleted"}


@router.get("/analytics", response_model=AdminAnalyticsResponse)
async def get_admin_analytics(
    days: int = Query(30, ge=7, le=365),
    db: Session = Depends(get_db_dep),
    current_user: User = Depends(require_superuser),
):
    """Get analytics data for charts"""
    return AdminCURD.get_analytics(db, days=days)
