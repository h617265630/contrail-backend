"""
Tests for RBAC permission and role checking logic.

Tests PermissionChecker, RoleChecker, has_permission, has_role.
"""
import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from app.core.deps import (
    PermissionChecker,
    RoleChecker,
    has_permission,
    has_role,
    get_current_user,
    get_current_active_user,
    credentials_exception,
)


# ─── PermissionChecker ───────────────────────────────────────────────────────

class TestPermissionChecker:
    """Tests for PermissionChecker dependency class."""

    def test_superuser_bypasses_all_permission_checks(self):
        """Superuser should pass without checking permissions."""
        checker = PermissionChecker(["some_permission", "another_permission"])
        superuser = MagicMock()
        superuser.is_superuser = True

        # Should return the user without raising
        result = checker(current_user=superuser)
        assert result == superuser
        # get_all_permissions should NOT be called
        superuser.get_all_permissions.assert_not_called()

    def test_user_with_required_permission_passes(self):
        """Regular user with all required permissions passes."""
        checker = PermissionChecker(["can_edit", "can_delete"])
        user = MagicMock()
        user.is_superuser = False
        user.get_all_permissions.return_value = ["can_edit", "can_delete", "can_view"]

        result = checker(current_user=user)
        assert result == user

    def test_user_missing_single_permission_raises_403(self):
        """User missing any required permission raises 403."""
        checker = PermissionChecker(["can_edit", "can_delete"])
        user = MagicMock()
        user.is_superuser = False
        user.get_all_permissions.return_value = ["can_view"]  # missing can_edit

        with pytest.raises(HTTPException) as exc_info:
            checker(current_user=user)
        assert exc_info.value.status_code == 403
        assert "权限不足" in exc_info.value.detail

    def test_user_missing_multiple_permissions_raises_403(self):
        """User missing multiple permissions raises 403."""
        checker = PermissionChecker(["can_edit", "can_delete", "can_admin"])
        user = MagicMock()
        user.is_superuser = False
        user.get_all_permissions.return_value = ["can_view"]  # missing all three

        with pytest.raises(HTTPException) as exc_info:
            checker(current_user=user)
        assert exc_info.value.status_code == 403

    def test_empty_required_permissions_list_passes(self):
        """No permissions required = always passes."""
        checker = PermissionChecker([])
        user = MagicMock()
        user.is_superuser = False
        user.get_all_permissions.return_value = []

        result = checker(current_user=user)
        assert result == user

    def test_permission_not_in_user_permissions_list_raises(self):
        """Permission code not present in user's permission list raises."""
        checker = PermissionChecker(["can_create_path"])
        user = MagicMock()
        user.is_superuser = False
        user.get_all_permissions.return_value = ["can_view", "can_edit"]  # no can_create_path

        with pytest.raises(HTTPException) as exc_info:
            checker(current_user=user)
        assert exc_info.value.status_code == 403
        assert "can_create_path" in exc_info.value.detail


# ─── RoleChecker ─────────────────────────────────────────────────────────────

class TestRoleChecker:
    """Tests for RoleChecker dependency class."""

    def test_superuser_bypasses_role_checks(self):
        """Superuser passes all role checks."""
        checker = RoleChecker(["admin", "editor"])
        superuser = MagicMock()
        superuser.is_superuser = True

        result = checker(current_user=superuser)
        assert result == superuser
        superuser.roles = []  # should not access roles

    def test_user_with_allowed_role_passes(self):
        """User with at least one allowed role passes."""
        admin_role = MagicMock()
        admin_role.code = "admin"
        checker = RoleChecker(["admin", "editor"])
        user = MagicMock()
        user.is_superuser = False
        user.roles = [admin_role]

        result = checker(current_user=user)
        assert result == user

    def test_user_with_no_allowed_role_raises_403(self):
        """User without any allowed role raises 403."""
        viewer_role = MagicMock()
        viewer_role.code = "viewer"
        checker = RoleChecker(["admin", "editor"])
        user = MagicMock()
        user.is_superuser = False
        user.roles = [viewer_role]

        with pytest.raises(HTTPException) as exc_info:
            checker(current_user=user)
        assert exc_info.value.status_code == 403
        assert "权限不足" in exc_info.value.detail

    def test_user_with_multiple_roles_passes_if_one_allowed(self):
        """User has viewer + editor; editor is allowed."""
        viewer_role = MagicMock()
        viewer_role.code = "viewer"
        editor_role = MagicMock()
        editor_role.code = "editor"
        checker = RoleChecker(["admin", "editor"])
        user = MagicMock()
        user.is_superuser = False
        user.roles = [viewer_role, editor_role]

        result = checker(current_user=user)
        assert result == user

    def test_user_with_no_roles_raises_403(self):
        """User with empty roles list raises 403."""
        checker = RoleChecker(["admin"])
        user = MagicMock()
        user.is_superuser = False
        user.roles = []

        with pytest.raises(HTTPException) as exc_info:
            checker(current_user=user)
        assert exc_info.value.status_code == 403

    def test_empty_allowed_roles_list_always_raises(self):
        """No allowed roles = everyone is denied."""
        checker = RoleChecker([])
        user = MagicMock()
        user.is_superuser = False
        user.roles = []

        with pytest.raises(HTTPException) as exc_info:
            checker(current_user=user)
        assert exc_info.value.status_code == 403


# ─── has_permission helper ────────────────────────────────────────────────────

class TestHasPermission:
    """Tests for has_permission factory function."""

    def test_superuser_always_passes(self):
        """has_permission('x') for superuser always returns user without raising."""
        superuser = MagicMock()
        superuser.is_superuser = True
        superuser.has_permission.return_value = False

        dep = has_permission("any_permission")
        result = dep(current_user=superuser)
        assert result == superuser
        # is_superuser check bypasses permission raise but the call still happens
        assert superuser.has_permission.called

    def test_user_with_permission_passes(self):
        """Regular user with the permission passes."""
        user = MagicMock()
        user.is_superuser = False
        user.has_permission.return_value = True

        dep = has_permission("can_create_resource")
        result = dep(current_user=user)
        assert result == user

    def test_user_without_permission_raises_403(self):
        """Regular user without required permission raises 403."""
        user = MagicMock()
        user.is_superuser = False
        user.has_permission.return_value = False

        dep = has_permission("can_delete_path")
        with pytest.raises(HTTPException) as exc_info:
            dep(current_user=user)
        assert exc_info.value.status_code == 403
        assert "can_delete_path" in exc_info.value.detail


# ─── has_role helper ─────────────────────────────────────────────────────────

class TestHasRole:
    """Tests for has_role factory function."""

    def test_superuser_always_passes(self):
        """has_role('x') for superuser always returns user."""
        superuser = MagicMock()
        superuser.is_superuser = True
        superuser.has_role.return_value = False  # irrelevant

        dep = has_role("any_role")
        result = dep(current_user=superuser)
        assert result == superuser

    def test_user_with_role_passes(self):
        """Regular user with required role passes."""
        user = MagicMock()
        user.is_superuser = False
        user.has_role.return_value = True

        dep = has_role("contributor")
        result = dep(current_user=user)
        assert result == user

    def test_user_without_role_raises_403(self):
        """Regular user without required role raises 403."""
        user = MagicMock()
        user.is_superuser = False
        user.has_role.return_value = False

        dep = has_role("moderator")
        with pytest.raises(HTTPException) as exc_info:
            dep(current_user=user)
        assert exc_info.value.status_code == 403
        assert "moderator" in exc_info.value.detail


# ─── get_current_active_user ─────────────────────────────────────────────────

class TestGetCurrentActiveUser:
    """Tests for get_current_active_user dependency."""

    def test_active_user_returns_user(self):
        """Active user passes through."""
        user = MagicMock()
        user.is_active = True

        result = get_current_active_user(current_user=user)
        assert result == user

    def test_inactive_user_raises_400(self):
        """Inactive user raises 400."""
        user = MagicMock()
        user.is_active = False

        with pytest.raises(HTTPException) as exc_info:
            get_current_active_user(current_user=user)
        assert exc_info.value.status_code == 400
        assert "Inactive user" in exc_info.value.detail


# ─── credentials_exception ───────────────────────────────────────────────────

class TestCredentialsException:
    """Tests for credentials_exception factory."""

    def test_returns_401_http_exception(self):
        """credentials_exception returns 401 with standard detail."""
        exc = credentials_exception()
        assert isinstance(exc, HTTPException)
        assert exc.status_code == 401
        assert exc.detail == "Could not validate credentials"
        assert "WWW-Authenticate" in exc.headers
