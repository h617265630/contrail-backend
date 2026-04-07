"""Add missing fields to user_learning_paths and fix invalid Base.metadata line

Revision ID: 20260407_0002
Revises: 20260407_0001
Create Date: 2026-04-07

Changes:
- Fix invalid Python code: removed stray "Base.metadata," line from model
- Add added_at TIMESTAMP DEFAULT NOW() NOT NULL
- Add is_pinned INTEGER DEFAULT 0 NOT NULL
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260407_0002"
down_revision: Union[str, Sequence[str], None] = "20260407_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add added_at column (nullable first, then set default)
    op.add_column(
        "user_learning_paths",
        sa.Column("added_at", sa.DateTime(), server_default=sa.text("NOW()"), nullable=False),
    )
    op.add_column(
        "user_learning_paths",
        sa.Column("is_pinned", sa.Integer(), server_default="0", nullable=False),
    )


def downgrade() -> None:
    op.drop_column("user_learning_paths", "is_pinned")
    op.drop_column("user_learning_paths", "added_at")
