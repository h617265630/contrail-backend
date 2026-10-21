"""
Tests for the fail-closed SECRET_KEY guard in app/core/config.py.

背景（2026-10-21 安全事件）：
    SECRET_KEY 的默认值 "dev-secret-change-me" 躺在公开 GitHub 仓库里半年了。
    它是 HS256 JWT 的签名密钥 —— 任何人拿到都能伪造 admin token。
    所以生产环境必须 fail closed：检测到默认值就直接拒绝启动，
    而不是"用默认值跑起来，等以后再改"。

覆盖的场景：
    - 本地开发：保持可用（只警告，不阻断）
    - 生产环境（Railway / Vercel / APP_ENV=production / APP_DEBUG=false）：
      默认 key → 抛 RuntimeError 拒绝启动
    - 生产环境 + 真实随机 key → 正常启动
"""

import importlib
import os

import pytest

import app.core.config as config_module
from app.core.config import (
    INSECURE_DEFAULT_SECRET_KEY,
    _is_production,
    _normalize_db_url,
)

# 所有会影响"是不是生产环境"判定的变量
PRODUCTION_MARKER_VARS = (
    "SECRET_KEY",
    "RAILWAY_ENVIRONMENT",
    "VERCEL",
    "FLY_APP_NAME",
    "RENDER",
    "DYNO",
    "APP_ENV",
    "ENVIRONMENT",
    "NODE_ENV",
    "APP_DEBUG",
)


@pytest.fixture
def clean_env(monkeypatch):
    """清掉所有生产标识变量，让每个用例从确定的状态出发。"""
    for var in PRODUCTION_MARKER_VARS:
        monkeypatch.delenv(var, raising=False)
    yield monkeypatch


def _reload_settings(monkeypatch, **env):
    """按给定的环境变量重新加载 config 模块，返回新的 settings 单例。"""
    for var in PRODUCTION_MARKER_VARS:
        monkeypatch.delenv(var, raising=False)
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    return importlib.reload(config_module)


# ─── _is_production ───────────────────────────────────────────────────────────

class TestIsProduction:
    """生产环境判定逻辑。"""

    def test_plain_local_env_is_not_production(self, clean_env):
        assert _is_production() is False

    @pytest.mark.parametrize(
        "var,value",
        [
            ("RAILWAY_ENVIRONMENT", "production"),
            ("VERCEL", "1"),
            ("FLY_APP_NAME", "learnpathly"),
            ("RENDER", "1"),
            ("DYNO", "web.1"),
            ("APP_ENV", "production"),
            ("APP_ENV", "prod"),
            ("ENVIRONMENT", "production"),
            ("NODE_ENV", "production"),
        ],
    )
    def test_platform_markers_mean_production(self, clean_env, var, value):
        clean_env.setenv(var, value)
        assert _is_production() is True

    def test_explicit_app_debug_false_means_production(self, clean_env):
        clean_env.setenv("APP_DEBUG", "false")
        assert _is_production() is True

    @pytest.mark.parametrize("value", ["true", "1", "yes", "on"])
    def test_app_debug_true_is_still_local(self, clean_env, value):
        clean_env.setenv("APP_DEBUG", value)
        assert _is_production() is False

    def test_app_env_development_is_not_production(self, clean_env):
        clean_env.setenv("APP_ENV", "development")
        assert _is_production() is False


# ─── fail-closed 守卫 ─────────────────────────────────────────────────────────

class TestSecretKeyGuard:
    """生产环境禁止使用公开的默认 SECRET_KEY。"""

    def test_default_key_is_the_known_public_value(self):
        """守卫判定的就是那个公开在 GitHub 上的默认值。"""
        assert INSECURE_DEFAULT_SECRET_KEY == "dev-secret-change-me"

    def test_local_dev_with_default_key_still_works(self, clean_env):
        """本地开发不能被阻断 —— 只警告。"""
        settings = _reload_settings(clean_env).settings
        assert settings.SECRET_KEY == INSECURE_DEFAULT_SECRET_KEY

    def test_production_with_default_key_fails_closed(self, clean_env):
        """生产环境 + 默认 key → 启动失败，而不是悄悄用公开密钥跑起来。"""
        with pytest.raises(RuntimeError) as exc:
            _reload_settings(clean_env, RAILWAY_ENVIRONMENT="production")
        assert "SECRET_KEY" in str(exc.value)

    def test_production_with_real_key_passes(self, clean_env):
        """生产环境 + 随机 key → 正常。"""
        real_key = "a" * 64
        settings = _reload_settings(
            clean_env, RAILWAY_ENVIRONMENT="production", SECRET_KEY=real_key
        ).settings
        assert settings.SECRET_KEY == real_key

    def test_app_debug_false_with_default_key_fails_closed(self, clean_env):
        """显式 APP_DEBUG=false 也按生产对待。"""
        with pytest.raises(RuntimeError):
            _reload_settings(clean_env, APP_DEBUG="false")

    def test_vercel_with_default_key_fails_closed(self, clean_env):
        """Vercel 环境 + 默认 key → 启动失败。"""
        with pytest.raises(RuntimeError):
            _reload_settings(clean_env, VERCEL="1")


# ─── 其它配置回归 ────────────────────────────────────────────────────────────

class TestOtherSettings:
    """确认改动没碰坏别的配置项。"""

    def test_cors_origins_default_is_local_only(self, clean_env):
        settings = _reload_settings(clean_env).settings
        assert settings.CORS_ORIGINS == [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ]

    def test_cors_origins_parses_csv(self, clean_env):
        settings = _reload_settings(
            clean_env,
            CORS_ORIGINS="https://www.learnpathly.com,http://localhost:5173",
        ).settings
        assert settings.CORS_ORIGINS == [
            "https://www.learnpathly.com",
            "http://localhost:5173",
        ]

    def test_algorithm_default_is_hs256(self, clean_env):
        settings = _reload_settings(clean_env).settings
        assert settings.ALGORITHM == "HS256"


# ─── DATABASE_URL 归一化 ──────────────────────────────────────────────────────

class TestDatabaseUrlNormalisation:
    """postgresql:// 必须显式升级成 postgresql+psycopg2://。

    SQLAlchemy 2.1 把 postgresql:// 的默认 driver 换成了 psycopg3，
    但 requirements.txt 只装了 psycopg2-binary → 启动即崩。
    """

    @pytest.mark.parametrize(
        "raw,expected",
        [
            (
                "postgresql://u:p@h:5432/db",
                "postgresql+psycopg2://u:p@h:5432/db",
            ),
            (
                "postgresql://u:p@h:5432/db?sslmode=require",
                "postgresql+psycopg2://u:p@h:5432/db?sslmode=require",
            ),
            ("postgres://u:p@h/db", "postgresql+psycopg2://u:p@h/db"),
        ],
    )
    def test_bare_postgres_urls_get_explicit_driver(self, clean_env, raw, expected):
        assert _normalize_db_url(raw) == expected

    @pytest.mark.parametrize(
        "raw",
        [
            "postgresql+psycopg2://u@h/db",
            "postgresql+psycopg://u@h/db",
            "sqlite:///local.db",
            "",
        ],
    )
    def test_explicit_or_non_postgres_urls_untouched(self, clean_env, raw):
        assert _normalize_db_url(raw) == raw

    def test_settings_applies_normalisation(self, clean_env):
        settings = _reload_settings(
            clean_env, DATABASE_URL="postgresql://u:p@h:5432/db"
        ).settings
        assert settings.DATABASE_URL == "postgresql+psycopg2://u:p@h:5432/db"

    def test_engine_resolves_to_installed_psycopg2(self, clean_env):
        """真实解析一次 dialect，确认落到的 driver 是依赖里装了的那一个。"""
        from sqlalchemy import create_engine

        settings = _reload_settings(
            clean_env, DATABASE_URL="postgresql://u:p@h:5432/db"
        ).settings
        engine = create_engine(settings.DATABASE_URL)
        assert engine.dialect.__module__.endswith("psycopg2")
