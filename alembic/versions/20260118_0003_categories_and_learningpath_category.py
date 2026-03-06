"""categories table + learning_paths.category_id

Revision ID: 20260118_0003
Revises: 20260117_0002
Create Date: 2026-01-18

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260118_0003"
down_revision = "20260117_0002"
branch_labels = None
depends_on = None


def _has_column(inspector: sa.Inspector, table: str, column: str) -> bool:
    return any(c["name"] == column for c in inspector.get_columns(table))


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # 1) categories table
    if not inspector.has_table("categories"):
        op.create_table(
            "categories",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("name", sa.String(length=100), nullable=False),
            sa.Column("code", sa.String(length=50), nullable=False),
            sa.Column("parent_id", sa.Integer(), sa.ForeignKey("categories.id"), nullable=True),
            sa.Column("level", sa.Integer(), nullable=False, server_default=sa.text("0")),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("is_leaf", sa.Boolean(), nullable=False, server_default=sa.text("true")),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
            sa.UniqueConstraint("name", name="uq_categories_name"),
            sa.UniqueConstraint("code", name="uq_categories_code"),
        )
        op.create_index("ix_categories_id", "categories", ["id"], unique=False)
        op.create_index("ix_categories_name", "categories", ["name"], unique=True)
        op.create_index("ix_categories_code", "categories", ["code"], unique=True)

    # 2) learning_paths.category_id
    if inspector.has_table("learning_paths"):
        with op.batch_alter_table("learning_paths") as batch:
            if not _has_column(inspector, "learning_paths", "category_id"):
                batch.add_column(sa.Column("category_id", sa.Integer(), nullable=True))
                batch.create_index("ix_learning_paths_category_id", ["category_id"], unique=False)
                batch.create_foreign_key(
                    "fk_learning_paths_category_id_categories",
                    "categories",
                    ["category_id"],
                    ["id"],
                )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if inspector.has_table("learning_paths") and _has_column(inspector, "learning_paths", "category_id"):
        with op.batch_alter_table("learning_paths") as batch:
            # best-effort: names may differ across DBs
            try:
                batch.drop_constraint("fk_learning_paths_category_id_categories", type_="foreignkey")
            except Exception:
                pass
            try:
                batch.drop_index("ix_learning_paths_category_id")
            except Exception:
                pass
            batch.drop_column("category_id")

    if inspector.has_table("categories"):
        # indexes may not exist if table pre-existed
        for ix in ("ix_categories_code", "ix_categories_name", "ix_categories_id"):
            try:
                op.drop_index(ix, table_name="categories")
            except Exception:
                pass
        op.drop_table("categories")
