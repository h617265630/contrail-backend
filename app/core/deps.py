"""
Dependency injection utilities for FastAPI routes.

Provides authentication, authorization, and database session dependencies:
- OAuth2 token-based authentication
- Optional and required user authentication
- Permission and role-based access control (RBAC)
"""

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
    """Dependency that yields a database session.

    Yields:
        Database session instance for use in route handlers.
    """
    yield from get_db()


def get_current_user_optional(
    db: Session = Depends(get_db_dep), request: Request = None
) -> Optional[User]:
    """
    Optional authentication dependency.

    Returns None if no valid token is present, instead of raising an exception.
    This is useful for endpoints that behave differently for authenticated vs
    anonymous users.

    Args:
        db: Database session.
        request: FastAPI request object to extract Authorization header.

    Returns:
        User object if valid token provided, None otherwise.
    """
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


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db_dep)) -> User:
    """
    Required authentication dependency.

    Validates the JWT token from the Authorization header and returns the
    associated user. Raises 401 if token is invalid or expired.

    Args:
        token: JWT token extracted from OAuth2 scheme.
        db: Database session.

    Returns:
        Authenticated User object.

    Raises:
        HTTPException: 401 if token is invalid, expired, or user not found.
    """
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


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency that ensures the authenticated user is active.

    Args:
        current_user: User from get_current_user dependency.

    Returns:
        The same user if active.

    Raises:
        HTTPException: 400 if user account is inactive.
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def credentials_exception() -> HTTPException:
    """
    Create a standard credentials validation error response.

    Returns:
        HTTPException with 401 status and standard error detail.
    """
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


# ============== Permission & Role Checkers ==============

class PermissionChecker:
    """
    Dependency class for checking if user has all required permissions.

    Superusers bypass all permission checks. Regular users must have
    all permissions specified in required_permissions.

    Args:
        required_permissions: List of permission codes the user must possess.
    """

    def __init__(self, required_permissions: Sequence[str]):
        self.required_permissions = list(required_permissions)

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        """
        Check if current user has all required permissions.

        Args:
            current_user: Authenticated user from dependency.

        Returns:
            User if all permissions present.

        Raises:
            HTTPException: 403 if any required permission is missing.
        """
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


class RoleChecker:
    """
    Dependency class for checking if user has any of the allowed roles.

    Superusers bypass all role checks. Regular users must have at least
    one of the roles specified in allowed_roles.

    Args:
        allowed_roles: List of role codes, any one of which grants access.
    """

    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        """
        Check if current user has any allowed role.

        Args:
            current_user: Authenticated user from dependency.

        Returns:
            User if has at least one allowed role.

        Raises:
            HTTPException: 403 if no allowed role is present.
        """
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


def has_permission(permission_code: str):
    """
    Factory function to create a permission check dependency.

    Args:
        permission_code: Single permission code required for access.

    Returns:
        Dependency function that validates the permission.
    """
    def permission_dependency(current_user: User = Depends(get_current_user)) -> User:
        if not current_user.has_permission(permission_code) and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"权限不足，需要权限: {permission_code}"
            )
        return current_user
    return permission_dependency


def has_role(role_code: str):
    """
    Factory function to create a role check dependency.

    Args:
        role_code: Single role code required for access.

    Returns:
        Dependency function that validates the role.
    """
    def role_dependency(current_user: User = Depends(get_current_user)) -> User:
        if not current_user.has_role(role_code) and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"权限不足，需要角色: {role_code}"
            )
        return current_user
    return role_dependency