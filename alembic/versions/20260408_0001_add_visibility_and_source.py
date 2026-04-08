"""Add visibility to resources and source to user_resource

Revision ID: 20260408_0001
Revises: 20260407_0004
Create Date: 2026-04-08
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260408_0001"
down_revision = "20260407_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Add visibility enum + column to resources
    resource_visibility = sa.Enum("private", "public", name="resource_visibility")
    resource_visibility.create(op.get_bind(), checkfirst=True)
    op.add_column(
        "resources",
        sa.Column("visibility", sa.Enum("private", "public", name="resource_visibility"), nullable=True),
    )

    # 2. Add source enum + column to user_resource
    user_resource_source = sa.Enum("created", "saved", name="user_resource_source")
    user_resource_source.create(op.get_bind(), checkfirst=True)
    op.add_column(
        "user_resource",
        sa.Column(
            "source",
            sa.Enum("created", "saved", name="user_resource_source"),
            nullable=False,
            server_default="saved",
        ),
    )


def downgrade() -> None:
    op.drop_column("user_resource", "source")
    op.drop_column("resources", "visibility")

    bind = op.get_bind()
    sa.Enum(name="user_resource_source").drop(bind, checkfirst=True)
    sa.Enum(name="resource_visibility").drop(bind, checkfirst=True)
