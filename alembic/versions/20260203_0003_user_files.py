"""user_files table for markdown/txt uploads

Revision ID: 20260203_0003
Revises: 20260131_0002
Create Date: 2026-02-03

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260203_0003"
down_revision = "20260131_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("user_files"):
        op.create_table(
            "user_files",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
            sa.Column("title", sa.String(length=200), nullable=True),
            sa.Column("file_type", sa.String(length=20), nullable=False),
            sa.Column("original_filename", sa.String(length=512), nullable=True),
            sa.Column("content_type", sa.String(length=200), nullable=True),
            sa.Column("size_bytes", sa.Integer(), nullable=True),
            sa.Column("file_url", sa.String(length=2048), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=True),
        )

    existing_indexes = {ix.get("name") for ix in inspector.get_indexes("user_files")} if inspector.has_table("user_files") else set()
    if "ix_user_files_id" not in existing_indexes:
        op.create_index("ix_user_files_id", "user_files", ["id"], unique=False)
    if "ix_user_files_user_id" not in existing_indexes:
        op.create_index("ix_user_files_user_id", "user_files", ["user_id"], unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("user_files"):
        return

    try:
        op.drop_index("ix_user_files_user_id", table_name="user_files")
    except Exception:
        pass
    try:
        op.drop_index("ix_user_files_id", table_name="user_files")
    except Exception:
        pass
    op.drop_table("user_files")
