"""Backfill creator_id for learning_paths from user_learning_paths

Revision ID: 20260409_0001
Revises: 20260408_0005
Create Date: 2026-04-09
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260409_0001"
down_revision = "20260408_0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add creator_id column if it doesn't exist (idempotent)
    conn = op.get_bind()
    result = conn.execute(
        sa.text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = 'learning_paths' AND column_name = 'creator_id'"
        )
    )
    if result.fetchone() is None:
        op.add_column(
            "learning_paths",
            sa.Column(
                "creator_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="SET NULL"),
                nullable=True,
            ),
        )

    # Backfill creator_id: set to the first user associated via user_learning_paths
    op.execute(
        sa.text(
            """
        UPDATE learning_paths lp
        SET creator_id = sub.user_id
        FROM (
            SELECT learning_path_id, MIN(user_id) as user_id
            FROM user_learning_paths
            GROUP BY learning_path_id
        ) sub
        WHERE lp.id = sub.learning_path_id
          AND lp.creator_id IS NULL
    """
        )
    )


def downgrade() -> None:
    op.execute(sa.text("UPDATE learning_paths SET creator_id = NULL"))
    op.drop_column("learning_paths", "creator_id")
