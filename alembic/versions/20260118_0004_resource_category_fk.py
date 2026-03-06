"""resources.category_id -> categories.id

Revision ID: 20260118_0004
Revises: 20260118_0003
Create Date: 2026-01-18

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260118_0004"
down_revision = "20260118_0003"
branch_labels = None
depends_on = None


def _has_column(inspector: sa.Inspector, table: str, column: str) -> bool:
    return any(c["name"] == column for c in inspector.get_columns(table))


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if inspector.has_table("resources"):
        with op.batch_alter_table("resources") as batch:
            if not _has_column(inspector, "resources", "category_id"):
                batch.add_column(sa.Column("category_id", sa.Integer(), nullable=True))
                batch.create_index("ix_resources_category_id", ["category_id"], unique=False)
                batch.create_foreign_key(
                    "fk_resources_category_id_categories",
                    "categories",
                    ["category_id"],
                    ["id"],
                )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if inspector.has_table("resources") and _has_column(inspector, "resources", "category_id"):
        with op.batch_alter_table("resources") as batch:
            try:
                batch.drop_constraint("fk_resources_category_id_categories", type_="foreignkey")
            except Exception:
                pass
            try:
                batch.drop_index("ix_resources_category_id")
            except Exception:
                pass
            batch.drop_column("category_id")
