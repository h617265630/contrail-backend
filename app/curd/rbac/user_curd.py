"""
User CRUD operations for RBAC system.

Provides database operations for user management including:
- User retrieval by ID, username, or email
- User creation with duplicate validation
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.rbac.user import User
from typing import Optional, List


class UserCURD:
    """CRUD operations for User model."""

    @staticmethod
    def get_user(db: Session, user_id: int) -> Optional[User]:
        """
        Retrieve a user by their ID.

        Args:
            db: Database session.
            user_id: Unique identifier of the user.

        Returns:
            User object if found, None otherwise.
        """
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """
        Retrieve a user by their username (case-insensitive).

        Args:
            db: Database session.
            username: Username to search for.

        Returns:
            User object if found, None otherwise.
        """
        normalized = (username or "").strip().lower()
        if not normalized:
            return None
        return db.query(User).filter(func.lower(User.username) == normalized).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """
        Retrieve a user by their email address (case-insensitive).

        Args:
            db: Database session.
            email: Email address to search for.

        Returns:
            User object if found, None otherwise.
        """
        normalized = (email or "").strip().lower()
        if not normalized:
            return None
        return db.query(User).filter(func.lower(User.email) == normalized).first()

    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Retrieve a paginated list of all users.

        Args:
            db: Database session.
            skip: Number of records to skip (offset).
            limit: Maximum number of records to return.

        Returns:
            List of User objects.
        """
        return db.query(User).offset(skip).limit(limit).all()

    @staticmethod
    def create_user(db: Session, username: str, email: str, hashed_password: str) -> User:
        """
        Create a new user.

        Note: Expects the password to be already hashed by the caller.
        Performs a defensive duplicate check on username and email before insert
        to provide a clearer error than a DB IntegrityError.

        Args:
            db: Database session.
            username: Desired username (will be normalized to lowercase).
            email: User's email address (will be normalized to lowercase).
            hashed_password: Pre-hashed password string.

        Returns:
            Newly created User object.

        Raises:
            ValueError: If username or email already exists in the database.
        """
        # Defensive duplicate checks (router also checks, but keep CURD robust)
        username_norm = (username or "").strip().lower()
        email_norm = (email or "").strip().lower()

        existing_by_username = db.query(User).filter(
            func.lower(User.username) == username_norm
        ).first()
        if existing_by_username:
            raise ValueError("Username already registered")

        existing_by_email = db.query(User).filter(
            func.lower(User.email) == email_norm
        ).first()
        if existing_by_email:
            raise ValueError("Email already registered")

        user = User(
            username=username_norm,
            email=email_norm,
            hashed_password=hashed_password,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    