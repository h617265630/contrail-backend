"""rebuild resources schema and extend path_items

Revision ID: 20260122_0008
Revises: 20260122_0007
Create Date: 2026-01-22

NOTE: This migration is DESTRUCTIVE for resource-related data.
It drops and recreates resource subtype tables and the resources table,
then recreates path_items with extended fields.

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260122_0008"
down_revision = "20260122_0007"
branch_labels = None
depends_on = None


def _has_table(inspector: sa.Inspector, name: str) -> bool:
    try:
        return inspector.has_table(name)
    except Exception:
        return name in inspector.get_table_names()


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    def _drop_table_if_exists_cascade(name: str) -> None:
        # Use CASCADE to drop dependent objects (FK constraints / dependent tables).
        # This is required for legacy DBs where videos is referenced by user_video, watch_history, etc.
        try:
            op.execute(sa.text(f'DROP TABLE IF EXISTS "{name}" CASCADE'))
        except Exception:
            pass

    # Drop tables that depend on resources/path_items first
    if _has_table(inspector, "progress"):
        op.drop_table("progress")

    if _has_table(inspector, "path_items"):
        op.drop_table("path_items")

    if _has_table(inspector, "user_resource"):
        op.drop_table("user_resource")

    # Drop legacy tables that may depend on videos/resources.
    # Use CASCADE to avoid failures like: DependentObjectsStillExist.
    for t in (
        "user_video_likes",
        "user_video",
        "watch_history",
        "video_category",
        # Old resource subtype tables
        "clips",
        "videos",
        "link_resources",
        "docs",
        "articles",
    ):
        _drop_table_if_exists_cascade(t)

    # Drop and recreate resources (best-effort)
    if _has_table(inspector, "resources"):
        _drop_table_if_exists_cascade("resources")

    # Recreate resources
    # Keep using the existing postgres enum name 'resourcetype' if present.
    if bind.dialect.name == "postgresql":
        # Ensure the enum type exists (create only if missing).
        # Also ensure required values exist (enum is case-sensitive in Postgres).
        try:
            op.execute(
                """
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'resourcetype') THEN
    CREATE TYPE resourcetype AS ENUM ('video', 'document', 'article', 'clip');
  END IF;
END$$;
"""
            )
        except Exception:
            pass

        # Best-effort: add missing enum values when type already exists.
        # (In legacy DBs, the enum may exist but miss some of these values or use different casing.)
        for val in ("video", "document", "article", "link", "clip"):
            try:
                op.execute(f"ALTER TYPE resourcetype ADD VALUE IF NOT EXISTS '{val}'")
            except Exception:
                pass

        # IMPORTANT: use dialect ENUM + create_type=False so SQLAlchemy won't emit CREATE TYPE.
        resourcetype = postgresql.ENUM(
            "video",
            "document",
            "article",
            "clip",
            name="resourcetype",
            create_type=False,
        )
    else:
        resourcetype = sa.Enum(
            "video",
            "document",
            "article",
            "clip",
            name="resourcetype",
        )

    op.create_table(
        "resources",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("resource_type", resourcetype, nullable=False),
        sa.Column("platform", sa.String(length=50), nullable=True),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("source_url", sa.String(length=2048), nullable=False),
        sa.Column("thumbnail", sa.String(length=1000), nullable=True),
        sa.Column("difficulty", sa.Integer(), nullable=True),
        sa.Column("tags", sa.JSON(), nullable=True),
        sa.Column("raw_meta", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_resources_resource_type", "resources", ["resource_type"], unique=False)
    op.create_index("ix_resources_platform", "resources", ["platform"], unique=False)

    # 1:1 extension tables
    op.create_table(
        "videos",
        sa.Column("resource_id", sa.Integer(), sa.ForeignKey("resources.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("duration", sa.Integer(), nullable=True),
        sa.Column("channel", sa.String(length=255), nullable=True),
        sa.Column("video_id", sa.String(length=100), nullable=True),
    )
    op.create_index("ix_videos_video_id", "videos", ["video_id"], unique=False)

    op.create_table(
        "docs",
        sa.Column("resource_id", sa.Integer(), sa.ForeignKey("resources.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("doc_type", sa.String(length=50), nullable=True),
        sa.Column("version", sa.String(length=50), nullable=True),
    )

    op.create_table(
        "articles",
        sa.Column("resource_id", sa.Integer(), sa.ForeignKey("resources.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("publisher", sa.String(length=255), nullable=True),
        sa.Column("published_at", sa.DateTime(), nullable=True),
    )

    # Recreate user_resource association
    op.create_table(
        "user_resource",
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("resource_id", sa.Integer(), sa.ForeignKey("resources.id"), primary_key=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("user_id", "resource_id", name="uq_user_resource"),
    )

    # Recreate path_items with extended fields
    op.create_table(
        "path_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("learning_path_id", sa.Integer(), sa.ForeignKey("learning_paths.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("resource_id", sa.Integer(), sa.ForeignKey("resources.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("stage", sa.String(length=100), nullable=True),
        sa.Column("purpose", sa.String(length=255), nullable=True),
        sa.Column("estimated_time", sa.Integer(), nullable=True),
        sa.Column("is_optional", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.UniqueConstraint("learning_path_id", "order_index", name="uq_learning_path_order"),
        sa.UniqueConstraint("learning_path_id", "resource_id", name="uq_learning_path_resource"),
    )

    # Recreate progress (depends on path_items)
    op.create_table(
        "progress",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("path_item_id", sa.Integer(), sa.ForeignKey("path_items.id", ondelete="CASCADE"), nullable=True),
        sa.Column("last_watched_time", sa.DateTime(), nullable=True),
        sa.Column("progress_percentage", sa.Integer(), nullable=True),
    )


def downgrade() -> None:
    # Downgrade is intentionally destructive as well; best-effort.
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    for t in (
        "progress",
        "path_items",
        "user_resource",
        "articles",
        "docs",
        "videos",
        "resources",
    ):
        if _has_table(inspector, t):
            op.drop_table(t)
