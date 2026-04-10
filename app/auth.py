"""
Authentication utilities for password hashing and JWT token management.

This module provides core authentication functionality including:
- Password hashing using bcrypt
- JWT access token creation and validation
"""

from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from typing import Optional

from app.core.config import settings

# 使用集中配置中的密钥与算法
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES  # token 有效期（分钟）

# Password hashing context using bcrypt algorithm
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a plain text password using bcrypt.

    Args:
        password: Plain text password to hash.

    Returns:
        Hashed password string.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a hashed password.

    Args:
        plain_password: Plain text password to verify.
        hashed_password: Hashed password to compare against.

    Returns:
        True if password matches, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token for the given subject.

    Args:
        subject: The token subject (typically user ID as string).
        expires_delta: Optional custom expiration time delta.
                      Defaults to ACCESS_TOKEN_EXPIRE_MINUTES if not provided.

    Returns:
        Encoded JWT token string.
    """
    to_encode = {"sub": str(subject)}
    now = datetime.now()
    expire = now + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"iat": now, "exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
