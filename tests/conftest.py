import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime


@pytest.fixture
def mock_db():
    """In-memory mock database session."""
    session = MagicMock()
    session.add = MagicMock()
    session.commit = MagicMock()
    session.refresh = MagicMock()
    session.query = MagicMock()
    return session


@pytest.fixture
def mock_user():
    """Mock user object with basic attributes."""
    user = MagicMock()
    user.id = 1
    user.username = "testuser"
    user.email = "test@example.com"
    user.is_active = True
    user.is_superuser = False
    user.roles = []
    user.get_all_permissions = MagicMock(return_value=[])
    user.has_permission = MagicMock(return_value=False)
    user.has_role = MagicMock(return_value=False)
    return user


@pytest.fixture
def mock_superuser():
    """Mock superuser object."""
    user = MagicMock()
    user.id = 99
    user.is_superuser = True
    user.roles = []
    user.get_all_permissions = MagicMock(return_value=["*"])
    return user
