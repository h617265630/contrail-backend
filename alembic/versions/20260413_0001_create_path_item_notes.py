"""Create path_item_notes table

Revision ID: 20260413_0001
Revises: 20260409_0001
Create Date: 2026-04-13
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260413_0001"
down_revision = "20260409_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "path_item_notes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("path_item_id", sa.Integer(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.ForeignKeyConstraint(
            ["path_item_id"], ["path_items.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "path_item_id", name="uq_path_item_note_user_path"),
    )
    op.create_index(
        "ix_path_item_notes_user_path",
        "path_item_notes",
        ["user_id", "path_item_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ix_path_item_notes_user_path", table_name="path_item_notes")
    op.drop_table("path_item_notes")
