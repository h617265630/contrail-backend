"""add content column to user_files

Revision ID: 20260203_0004
Revises: 20260203_0003
Create Date: 2026-02-03

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260203_0004"
down_revision = "20260203_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("user_files"):
        return

    cols = {c["name"] for c in inspector.get_columns("user_files")}
    if "content" not in cols:
        op.add_column("user_files", sa.Column("content", sa.Text(), nullable=True))


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("user_files"):
        return

    cols = {c["name"] for c in inspector.get_columns("user_files")}
    if "content" in cols:
        try:
            op.drop_column("user_files", "content")
        except Exception:
            pass
