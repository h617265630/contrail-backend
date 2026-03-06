"""drop legacy video tables

Revision ID: 20260122_0009
Revises: 20260122_0008
Create Date: 2026-01-22

NOTE: This migration removes legacy tables that are no longer used after the
resource schema rebuild.

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260122_0009"
down_revision = "20260122_0008"
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

    # Drop dependents first
    for t in (
        "user_video_likes",
        "watch_history",
        "user_video",
        "video_category",
    ):
        if _has_table(inspector, t):
            op.drop_table(t)


def downgrade() -> None:
    # Intentionally no-op (legacy tables are not recreated)
    pass
