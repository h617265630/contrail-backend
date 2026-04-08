"""Add fork lineage and status fields to learning_paths

Revision ID: 20260408_0002
Revises: 20260408_0001
Create Date: 2026-04-08
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260408_0002"
down_revision = "20260408_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Fork lineage
    op.add_column("learning_paths", sa.Column("parent_id", sa.Integer(), sa.ForeignKey("learning_paths.id", ondelete="SET NULL"), nullable=True))
    op.add_column("learning_paths", sa.Column("root_id", sa.Integer(), sa.ForeignKey("learning_paths.id", ondelete="SET NULL"), nullable=True))
    op.create_index("ix_learning_paths_parent_id", "learning_paths", ["parent_id"])
    op.create_index("ix_learning_paths_root_id", "learning_paths", ["root_id"])

    # 2. 发布状态
    path_status = sa.Enum("draft", "published", "archived", name="pathstatus")
    path_status.create(op.get_bind(), checkfirst=True)
    op.add_column("learning_paths", sa.Column("status", sa.Enum("draft", "published", "archived", name="pathstatus"), nullable=False, server_default="draft"))
    op.add_column("learning_paths", sa.Column("published_at", sa.DateTime(), nullable=True))

    # 3. 统计字段
    op.add_column("learning_paths", sa.Column("fork_count", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("learning_paths", sa.Column("like_count", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("learning_paths", sa.Column("view_count", sa.Integer(), nullable=False, server_default="0"))


def downgrade() -> None:
    op.drop_index("ix_learning_paths_root_id", "learning_paths")
    op.drop_index("ix_learning_paths_parent_id", "learning_paths")
    op.drop_column("learning_paths", "view_count")
    op.drop_column("learning_paths", "like_count")
    op.drop_column("learning_paths", "fork_count")
    op.drop_column("learning_paths", "published_at")
    op.drop_column("learning_paths", "status")
    op.drop_column("learning_paths", "root_id")
    op.drop_column("learning_paths", "parent_id")

    sa.Enum(name="pathstatus").drop(op.get_bind(), checkfirst=True)
