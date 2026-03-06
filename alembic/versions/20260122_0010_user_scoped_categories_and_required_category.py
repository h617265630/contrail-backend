"""user-scoped categories + required category_id for resources/learning_paths

Revision ID: 20260122_0010
Revises: 20260122_0009
Create Date: 2026-01-22

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260122_0010"
down_revision = "20260122_0009"
branch_labels = None
depends_on = None


def _has_column(inspector: sa.Inspector, table: str, column: str) -> bool:
    return any(c["name"] == column for c in inspector.get_columns(table))


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # 1) categories: add user scoping fields
    if inspector.has_table("categories"):
        with op.batch_alter_table("categories") as batch:
            if not _has_column(inspector, "categories", "is_system"):
                batch.add_column(sa.Column("is_system", sa.Boolean(), nullable=True))
            if not _has_column(inspector, "categories", "owner_user_id"):
                batch.add_column(sa.Column("owner_user_id", sa.Integer(), nullable=True))

        # best-effort backfill for existing default categories
        try:
            op.execute(sa.text("UPDATE categories SET is_system = TRUE WHERE is_system IS NULL"))
        except Exception:
            pass

        # Create FK to users (best-effort)
        with op.batch_alter_table("categories") as batch:
            try:
                batch.create_foreign_key(
                    "fk_categories_owner_user_id_users",
                    "users",
                    ["owner_user_id"],
                    ["id"],
                )
            except Exception:
                pass

        # Make is_system NOT NULL with default TRUE
        with op.batch_alter_table("categories") as batch:
            try:
                batch.alter_column(
                    "is_system",
                    existing_type=sa.Boolean(),
                    nullable=False,
                    server_default=sa.text("true"),
                )
            except Exception:
                pass

    # 2) resources.category_id (required)
    if inspector.has_table("resources"):
        # Add column if missing
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

        # Backfill to default category: code='other'
        try:
            op.execute(
                sa.text(
                    "UPDATE resources SET category_id = (SELECT id FROM categories WHERE code = :code LIMIT 1) "
                    "WHERE category_id IS NULL"
                ).bindparams(code="other")
            )
        except Exception:
            pass

        # Make NOT NULL (enforced at DB)
        with op.batch_alter_table("resources") as batch:
            try:
                batch.alter_column(
                    "category_id",
                    existing_type=sa.Integer(),
                    nullable=False,
                )
            except Exception:
                pass

    # 3) learning_paths.category_id (required)
    if inspector.has_table("learning_paths"):
        # backfill (column already exists)
        if _has_column(inspector, "learning_paths", "category_id"):
            try:
                op.execute(
                    sa.text(
                        "UPDATE learning_paths SET category_id = (SELECT id FROM categories WHERE code = :code LIMIT 1) "
                        "WHERE category_id IS NULL"
                    ).bindparams(code="other")
                )
            except Exception:
                pass

            with op.batch_alter_table("learning_paths") as batch:
                try:
                    batch.alter_column(
                        "category_id",
                        existing_type=sa.Integer(),
                        nullable=False,
                    )
                except Exception:
                    pass


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if inspector.has_table("learning_paths") and _has_column(inspector, "learning_paths", "category_id"):
        with op.batch_alter_table("learning_paths") as batch:
            try:
                batch.alter_column("category_id", existing_type=sa.Integer(), nullable=True)
            except Exception:
                pass

    if inspector.has_table("resources") and _has_column(inspector, "resources", "category_id"):
        with op.batch_alter_table("resources") as batch:
            try:
                batch.alter_column("category_id", existing_type=sa.Integer(), nullable=True)
            except Exception:
                pass

    if inspector.has_table("categories"):
        with op.batch_alter_table("categories") as batch:
            try:
                batch.drop_constraint("fk_categories_owner_user_id_users", type_="foreignkey")
            except Exception:
                pass
            for col in ("owner_user_id", "is_system"):
                if _has_column(inspector, "categories", col):
                    try:
                        batch.drop_column(col)
                    except Exception:
                        pass
