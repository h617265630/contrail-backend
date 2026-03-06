# backend/app/crud/user.py
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.rbac.user import User
# from app.auth import hash_password
# from app.schemas.user import UserCreate
from typing import Optional,List
# from sqlalchemy.orm import selectinload

class UserCURD:
    @staticmethod
    def get_user(db: Session, user_id: int)->Optional[User]:
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_username(db: Session, username: str)->Optional[User]:
        normalized = (username or "").strip().lower()
        if not normalized:
            return None
        return db.query(User).filter(func.lower(User.username) == normalized).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str)->Optional[User]:
        normalized = (email or "").strip().lower()
        if not normalized:
            return None
        return db.query(User).filter(func.lower(User.email) == normalized).first()


    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100)->List[User]:
        return db.query(User).offset(skip).limit(limit).all()


    @staticmethod
    def create_user(db: Session, username: str, email: str, hashed_password: str)->User:
        """
        Create a new user.

        Expects the password to be already hashed by the caller.
        Performs a defensive duplicate check on username and email before insert
        to provide a clearer error than a DB IntegrityError.
        """

        # Defensive duplicate checks (router also checks, but keep CURD robust)
        username_norm = (username or "").strip().lower()
        email_norm = (email or "").strip().lower()

        existing_by_username = db.query(User).filter(func.lower(User.username) == username_norm).first()
        if existing_by_username:
            raise ValueError("Username already registered")

        existing_by_email = db.query(User).filter(func.lower(User.email) == email_norm).first()
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
    
    