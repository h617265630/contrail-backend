"""
Centralized application configuration.

Loads environment variables (via python-dotenv if available) and provides
typed settings with sensible defaults for local development.
"""

import os
from dataclasses import dataclass

try:
	# Optional: load .env if available
	from dotenv import load_dotenv
	load_dotenv()
except Exception:
	pass


def _parse_csv_env(name: str, default: str = "") -> list[str]:
	raw = os.environ.get(name, default)
	if not raw:
		return []
	return [item.strip() for item in raw.split(",") if item.strip()]


@dataclass
class Settings:
	# Database
	DATABASE_URL: str = os.environ.get(
		"DATABASE_URL",
		"postgresql://postgres:burnme@localhost/db",
	)
	SQL_ECHO: bool = os.environ.get("SQL_ECHO", "true").lower() in {"1", "true", "yes", "on"}

	# Auth / Security
	SECRET_KEY: str = os.environ.get("SECRET_KEY", "dev-secret-change-me")
	ALGORITHM: str = os.environ.get("ALGORITHM", "HS256")
	ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

	# OAuth (Google)
	GOOGLE_CLIENT_ID: str = os.environ.get("GOOGLE_CLIENT_ID", "")
	GOOGLE_CLIENT_SECRET: str = os.environ.get("GOOGLE_CLIENT_SECRET", "")

	FASTSPRING_WEBHOOK_SECRET: str = os.environ.get("FASTSPRING_WEBHOOK_SECRET", "")

	# Runtime
	APP_DEBUG: bool = os.environ.get("APP_DEBUG", "false").lower() in {"1", "true", "yes", "on"}
	CORS_ORIGINS: list[str] = None  # type: ignore[assignment]

	def __post_init__(self):
		# comma-separated list, e.g. "https://your-frontend.vercel.app,http://localhost:5173"
		self.CORS_ORIGINS = _parse_csv_env(
			"CORS_ORIGINS",
			"http://localhost:5173,http://127.0.0.1:5173",
		)


# Singleton settings instance
settings = Settings()
