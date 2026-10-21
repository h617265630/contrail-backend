"""
Centralized application configuration.

Loads environment variables (via python-dotenv if available) and provides
typed settings with sensible defaults for local development.
"""

import logging
import os
from dataclasses import dataclass

try:
	# Optional: load .env if available
	from dotenv import load_dotenv
	load_dotenv()
except Exception:
	pass

logger = logging.getLogger(__name__)

# 这个默认值在公开的 GitHub 仓库里躺了半年，任何人都能拿到。
# 它是 HS256 JWT 的签名密钥 —— 用它签发的 token 可以被任何人伪造成 admin。
# 生产环境必须显式配置真正的随机密钥，见 __post_init__ 里的 fail-closed 检查。
INSECURE_DEFAULT_SECRET_KEY = "dev-secret-change-me"


def _parse_csv_env(name: str, default: str = "") -> list[str]:
	raw = os.environ.get(name, default)
	if not raw:
		return []
	return [item.strip() for item in raw.split(",") if item.strip()]


def _normalize_db_url(url: str) -> str:
	"""把 postgresql:// 显式升级成 postgresql+psycopg2://。

	背景（2026-10-22 巡检发现）：
	  SQLAlchemy 2.1 把 postgresql:// 的默认 driver 从 psycopg2 改成了 psycopg3，
	  但 requirements.txt 只装了 psycopg2-binary。于是新环境里
	  create_engine("postgresql://...") 会抛
	  ModuleNotFoundError: No module named 'psycopg' —— 启动即崩。

	  显式写死 driver 就不依赖 SQLAlchemy 的默认值了，
	  线上已有的 DATABASE_URL（postgresql://...）也不用改。
	"""
	if not url:
		return url
	if url.startswith("postgresql://"):
		return "postgresql+psycopg2://" + url[len("postgresql://") :]
	if url.startswith("postgres://"):
		return "postgresql+psycopg2://" + url[len("postgres://") :]
	return url


def _is_production() -> bool:
	"""判断当前是否运行在生产环境。

	只认明确的生产标识，避免本地开发因为没配 .env 就被误判成生产。
	"""
	# 平台注入的环境变量
	for var in ("RAILWAY_ENVIRONMENT", "VERCEL", "FLY_APP_NAME", "RENDER", "DYNO"):
		if os.environ.get(var):
			return True
	# 显式声明的环境名
	for var in ("APP_ENV", "ENVIRONMENT", "NODE_ENV"):
		if os.environ.get(var, "").strip().lower() in {"production", "prod"}:
			return True
	# 显式关掉 debug 也按生产对待
	if "APP_DEBUG" in os.environ and os.environ["APP_DEBUG"].strip().lower() in {
		"0",
		"false",
		"no",
		"off",
	}:
		return True
	return False


@dataclass
class Settings:
	# Database
	# 默认连接本地 PostgreSQL，线上 Railway 通过环境变量 DATABASE_URL 指向 Supabase
	DATABASE_URL: str = os.environ.get(
		"DATABASE_URL",
		"postgresql://postgres:burnme@localhost:5432/db",
	)
	SQL_ECHO: bool = os.environ.get("SQL_ECHO", "true").lower() in {"1", "true", "yes", "on"}

	# Auth / Security
	SECRET_KEY: str = os.environ.get("SECRET_KEY", INSECURE_DEFAULT_SECRET_KEY)
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

		# 显式指定 psycopg2 driver，别依赖 SQLAlchemy 的默认值
		# （2.1+ 默认走 psycopg3，而依赖里只装了 psycopg2-binary）
		self.DATABASE_URL = _normalize_db_url(self.DATABASE_URL)

		# Fail closed: 生产环境绝不允许使用公开的默认签名密钥。
		# 宁可启动失败，也不能让一个谁都能伪造 admin token 的服务跑起来。
		if self.SECRET_KEY == INSECURE_DEFAULT_SECRET_KEY:
			msg = (
				f"SECRET_KEY 仍是公开默认值 '{INSECURE_DEFAULT_SECRET_KEY}' —— "
				"任何人都能用它伪造 admin token。请生成随机密钥并注入环境变量"
				"（python -c \"import secrets; print(secrets.token_urlsafe(48))\"）。"
			)
			if _is_production():
				raise RuntimeError(msg)
			logger.warning("⚠️ %s", msg)


# Singleton settings instance
settings = Settings()
