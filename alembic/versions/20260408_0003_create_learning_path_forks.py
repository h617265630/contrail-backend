"""Create learning_path_forks table

Revision ID: 20260408_0003
Revises: 20260408_0002
Create Date: 2026-04-08
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260408_0003"
down_revision = "20260408_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "learning_path_forks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source_path_id", sa.Integer(), sa.ForeignKey("learning_paths.id", ondelete="CASCADE"), nullable=False),
        sa.Column("forked_path_id", sa.Integer(), sa.ForeignKey("learning_paths.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("forked_path_id", name="uq_fork_forked_path"),
    )
    op.create_index("ix_learning_path_forks_source_path_id", "learning_path_forks", ["source_path_id"])
    op.create_index("ix_learning_path_forks_forked_path_id", "learning_path_forks", ["forked_path_id"])
    op.create_index("ix_learning_path_forks_user_id", "learning_path_forks", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_learning_path_forks_user_id", "learning_path_forks")
    op.drop_index("ix_learning_path_forks_forked_path_id", "learning_path_forks")
    op.drop_index("ix_learning_path_forks_source_path_id", "learning_path_forks")
    op.drop_table("learning_path_forks")
