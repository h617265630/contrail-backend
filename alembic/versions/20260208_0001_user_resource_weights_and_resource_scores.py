"""user_resource weights tracking and resource community scores

Revision ID: 20260208_0001
Revises: 20260203_0004
Create Date: 2026-02-08

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260208_0001"
down_revision = "20260203_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if inspector.has_table("user_resource"):
        cols = {c["name"] for c in inspector.get_columns("user_resource")}

        if "manual_weight" not in cols:
            op.add_column("user_resource", sa.Column("manual_weight", sa.Integer(), nullable=True))
        if "behavior_weight" not in cols:
            op.add_column("user_resource", sa.Column("behavior_weight", sa.Integer(), nullable=True))
        if "effective_weight" not in cols:
            op.add_column("user_resource", sa.Column("effective_weight", sa.Integer(), nullable=True))

        if "added_at" not in cols:
            op.add_column("user_resource", sa.Column("added_at", sa.DateTime(), nullable=True))
        if "last_opened" not in cols:
            op.add_column("user_resource", sa.Column("last_opened", sa.DateTime(), nullable=True))
        if "open_count" not in cols:
            op.add_column(
                "user_resource",
                sa.Column("open_count", sa.Integer(), nullable=False, server_default="0"),
            )
        if "completion_status" not in cols:
            op.add_column(
                "user_resource",
                sa.Column("completion_status", sa.Boolean(), nullable=False, server_default=sa.text("false")),
            )

        cols = {c["name"] for c in inspector.get_columns("user_resource")}
        if "added_at" in cols and "created_at" in cols:
            op.execute(sa.text("UPDATE user_resource SET added_at = created_at WHERE added_at IS NULL"))

        if "open_count" in cols:
            try:
                op.alter_column("user_resource", "open_count", server_default=None)
            except Exception:
                pass
        if "completion_status" in cols:
            try:
                op.alter_column("user_resource", "completion_status", server_default=None)
            except Exception:
                pass

    if inspector.has_table("resources"):
        cols = {c["name"] for c in inspector.get_columns("resources")}

        if "community_score" not in cols:
            op.add_column(
                "resources",
                sa.Column("community_score", sa.Integer(), nullable=False, server_default="0"),
            )
        if "save_count" not in cols:
            op.add_column(
                "resources",
                sa.Column("save_count", sa.Integer(), nullable=False, server_default="0"),
            )
        if "trending_score" not in cols:
            op.add_column(
                "resources",
                sa.Column("trending_score", sa.Integer(), nullable=False, server_default="0"),
            )

        cols = {c["name"] for c in inspector.get_columns("resources")}
        for c in ("community_score", "save_count", "trending_score"):
            if c in cols:
                try:
                    op.alter_column("resources", c, server_default=None)
                except Exception:
                    pass


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if inspector.has_table("user_resource"):
        cols = {c["name"] for c in inspector.get_columns("user_resource")}
        for c in (
            "completion_status",
            "open_count",
            "last_opened",
            "added_at",
            "effective_weight",
            "behavior_weight",
            "manual_weight",
        ):
            if c in cols:
                try:
                    op.drop_column("user_resource", c)
                except Exception:
                    pass

    if inspector.has_table("resources"):
        cols = {c["name"] for c in inspector.get_columns("resources")}
        for c in ("trending_score", "save_count", "community_score"):
            if c in cols:
                try:
                    op.drop_column("resources", c)
                except Exception:
                    pass
