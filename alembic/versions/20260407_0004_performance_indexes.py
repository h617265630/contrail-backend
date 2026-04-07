"""Performance indexes: path_items FK, user_resource filter, learning_paths public

Revision ID: 20260407_0004
Revises: 20260407_0003
Create Date: 2026-04-07

Index additions:
- path_items: FK indexes on learning_path_id and resource_id (may already exist)
- user_resource: composite index on (user_id, added_at) for sort,
  partial index on (user_id, completion_status) for filtered queries
- learning_paths: partial index on (is_public, is_active) for public path listing
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260407_0004"
down_revision: Union[str, Sequence[str], None] = "20260407_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ---- path_items: FK indexes ----
    # Use IF NOT EXISTS — these may already exist from a partially-failed
    # prior run that used CONCURRENTLY (which errored mid-transaction but
    # created the index before the rollback).
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_path_items_learning_path_id "
        "ON path_items (learning_path_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_path_items_resource_id "
        "ON path_items (resource_id)"
    )

    # ---- user_resource: added_at sort index ----
    # list_my_resources sorts by added_at to assign user_seq
    op.create_index(
        "ix_user_resource_user_added",
        "user_resource",
        ["user_id", "added_at"],
        unique=False,
    )

    # ---- user_resource: completion_status partial index ----
    # Partial index: only index rows where completion_status = true.
    # This keeps the index tiny while speeding up "show completed" filters.
    op.execute(
        """
        CREATE INDEX ix_user_resource_completion
        ON user_resource(user_id, completion_status)
        WHERE completion_status = true
        """
    )

    # ---- learning_paths: public+active partial index ----
    # list_public_learning_paths filters on is_public AND is_active
    op.execute(
        """
        CREATE INDEX ix_learning_paths_public_active
        ON learning_paths(is_public, is_active)
        WHERE is_public = true AND is_active = true
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_learning_paths_public_active")
    op.execute("DROP INDEX IF EXISTS ix_user_resource_completion")
    op.drop_index("ix_user_resource_user_added", table_name="user_resource")
    op.drop_index("ix_path_items_resource_id", table_name="path_items")
    op.drop_index("ix_path_items_learning_path_id", table_name="path_items")
