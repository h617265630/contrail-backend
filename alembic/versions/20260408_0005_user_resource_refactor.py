"""Refactor user_resource: remove custom_* fields, add category_id override

Revision ID: 20260408_0005
Revises: 20260408_0004
Create Date: 2026-04-08
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260408_0005"
down_revision = "20260408_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. 删除多余的覆盖字段（title/summary/thumbnail 存在 resources 表，不可修改）
    op.drop_column("user_resource", "custom_thumbnail")
    op.drop_column("user_resource", "custom_summary")
    op.drop_column("user_resource", "custom_title")

    # 2. 新增用户自定义分类覆盖
    op.add_column("user_resource", sa.Column("category_id", sa.Integer(), sa.ForeignKey("categories.id"), nullable=True))


def downgrade() -> None:
    op.drop_column("user_resource", "category_id")
    op.add_column("user_resource", sa.Column("custom_title", sa.String(length=500), nullable=True))
    op.add_column("user_resource", sa.Column("custom_summary", sa.Text(), nullable=True))
    op.add_column("user_resource", sa.Column("custom_thumbnail", sa.String(length=1000), nullable=True))
