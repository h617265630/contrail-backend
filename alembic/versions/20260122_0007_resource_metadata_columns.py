"""persist resource metadata columns

Revision ID: 20260122_0007
Revises: 20260122_0006
Create Date: 2026-01-22

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260122_0007"
down_revision = "20260122_0006b"
branch_labels = None
depends_on = None


def _has_column(inspector: sa.Inspector, table: str, column: str) -> bool:
    return any(c["name"] == column for c in inspector.get_columns(table))


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("resources"):
        return

    if not _has_column(inspector, "resources", "platform"):
        op.add_column("resources", sa.Column("platform", sa.String(length=50), nullable=True))

    if not _has_column(inspector, "resources", "author"):
        op.add_column("resources", sa.Column("author", sa.String(length=200), nullable=True))

    if not _has_column(inspector, "resources", "video_id"):
        op.add_column("resources", sa.Column("video_id", sa.String(length=100), nullable=True))

    if not _has_column(inspector, "resources", "duration_seconds"):
        op.add_column("resources", sa.Column("duration_seconds", sa.Integer(), nullable=True))


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("resources"):
        return

    # Best-effort downgrade; ignore failures for databases that don't support DROP COLUMN.
    for col in ("duration_seconds", "video_id", "author", "platform"):
        if _has_column(inspector, "resources", col):
            try:
                op.drop_column("resources", col)
            except Exception:
                pass
