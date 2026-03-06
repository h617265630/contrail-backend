from __future__ import annotations

from dataclasses import dataclass

from email_validator import EmailNotValidError, validate_email

USERNAME_MIN_LEN = 3
USERNAME_MAX_LEN = 32
PASSWORD_MIN_LEN = 8


@dataclass(frozen=True)
class NormalizedCredentials:
    username: str
    email: str


def normalize_username(value: str) -> str:
    if value is None:
        return ""
    return value.strip().lower()


def normalize_email(value: str) -> str:
    if value is None:
        return ""
    # validate_email will also normalize (e.g. casefold domain) but we still lower for consistency
    normalized = value.strip().lower()
    try:
        validate_email(normalized, check_deliverability=False)
    except EmailNotValidError as exc:
        raise ValueError("Invalid email format") from exc
    return normalized


def validate_username(username: str) -> str:
    normalized = normalize_username(username)
    if not normalized:
        raise ValueError("Username is required")
    if not (USERNAME_MIN_LEN <= len(normalized) <= USERNAME_MAX_LEN):
        raise ValueError(f"Username length must be {USERNAME_MIN_LEN}-{USERNAME_MAX_LEN}")
    return normalized


def validate_password(password: str) -> str:
    if password is None:
        raise ValueError("Password is required")
    # do not strip actual password for hashing; only use strip for emptiness check
    if not password.strip():
        raise ValueError("Password is required")
    if len(password) < PASSWORD_MIN_LEN:
        raise ValueError(f"Password length must be >= {PASSWORD_MIN_LEN}")
    return password
