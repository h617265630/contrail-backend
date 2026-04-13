"""Create resource_summary_cache table

Revision ID: 20260414_0001
Revises: 20260413_0001
Create Date: 2026-04-14
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260414_0001"
down_revision = "20260413_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "resource_summary_cache",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("cache_key", sa.String(length=64), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("topic", sa.Text(), nullable=False),
        sa.Column("title", sa.Text(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("key_points", sa.Text(), nullable=True),
        sa.Column("difficulty", sa.String(length=32), nullable=True),
        sa.Column("resource_type", sa.String(length=32), nullable=True),
        sa.Column("learning_stage", sa.String(length=32), nullable=True),
        sa.Column("estimated_minutes", sa.Integer(), nullable=True),
        sa.Column("image", sa.Text(), nullable=True),
        sa.Column(
            "fetched_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("cache_key", name="uq_resource_summary_cache_key"),
    )
    op.create_index(
        "ix_resource_summary_cache_url_topic",
        "resource_summary_cache",
        ["url", "topic"],
        unique=False,
    )
    op.create_index(
        "ix_resource_summary_cache_cache_key",
        "resource_summary_cache",
        ["cache_key"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_resource_summary_cache_cache_key", table_name="resource_summary_cache")
    op.drop_index("ix_resource_summary_cache_url_topic", table_name="resource_summary_cache")
    op.drop_table("resource_summary_cache")
