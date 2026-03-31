"""Increase resources.title length to 500

Revision ID: 20260330_0001
Revises: 20260208_0001
Create Date: 2026-03-30 14:56:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260330_0001"
down_revision: Union[str, Sequence[str], None] = "20260208_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "resources",
        "title",
        existing_type=sa.String(length=200),
        type_=sa.String(length=500),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "resources",
        "title",
        existing_type=sa.String(length=500),
        type_=sa.String(length=200),
        existing_nullable=False,
    )
