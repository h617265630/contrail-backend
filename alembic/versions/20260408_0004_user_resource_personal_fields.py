"""Add personal fields to user_resource

Revision ID: 20260408_0004
Revises: 20260408_0003
Create Date: 2026-04-08
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260408_0004"
down_revision = "20260408_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("user_resource", sa.Column("custom_notes", sa.Text(), nullable=True))
    op.add_column("user_resource", sa.Column("custom_tags", sa.JSON(), nullable=True))
    op.add_column("user_resource", sa.Column("personal_rating", sa.Integer(), nullable=True))
    op.add_column("user_resource", sa.Column("is_favorite", sa.Boolean(), nullable=False, server_default="0"))


def downgrade() -> None:
    op.drop_column("user_resource", "is_favorite")
    op.drop_column("user_resource", "personal_rating")
    op.drop_column("user_resource", "custom_tags")
    op.drop_column("user_resource", "custom_notes")
