"""learning_paths.cover_image_url

Revision ID: 20260119_0005
Revises: 20260118_0004
Create Date: 2026-01-19

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260119_0005"
down_revision = "20260118_0004"
branch_labels = None
depends_on = None


def _has_column(inspector: sa.Inspector, table: str, column: str) -> bool:
    return any(c["name"] == column for c in inspector.get_columns(table))


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if inspector.has_table("learning_paths"):
        with op.batch_alter_table("learning_paths") as batch:
            if not _has_column(inspector, "learning_paths", "cover_image_url"):
                batch.add_column(sa.Column("cover_image_url", sa.String(length=2048), nullable=True))


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if inspector.has_table("learning_paths") and _has_column(inspector, "learning_paths", "cover_image_url"):
        with op.batch_alter_table("learning_paths") as batch:
            batch.drop_column("cover_image_url")
