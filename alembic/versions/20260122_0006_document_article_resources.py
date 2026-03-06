"""document/article resource subtypes (joined-table)

Revision ID: 20260122_0006b
Revises: 20260122_0006
Create Date: 2026-01-22

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260122_0006b"
down_revision = "20260122_0006"
branch_labels = None
depends_on = None


def _has_column(inspector: sa.Inspector, table: str, column: str) -> bool:
    return any(c["name"] == column for c in inspector.get_columns(table))


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # 1) Extend enum type in Postgres
    if bind.dialect.name == "postgresql":
        op.execute("ALTER TYPE resourcetype ADD VALUE IF NOT EXISTS 'document'")
        op.execute("ALTER TYPE resourcetype ADD VALUE IF NOT EXISTS 'article'")

    # 2) Migrate legacy docs table if it exists (non-Resource-backed)
    # If an old docs table exists, rename it to docs_legacy and create a new docs
    # joined-table that references resources.id.
    if inspector.has_table("docs"):
        cols = {c["name"] for c in inspector.get_columns("docs")}
        # Old legacy docs table typically has columns like: id, name, description
        # New joined-table docs must have: id (FK resources.id), url/source/category/thumbnail_url
        is_legacy = "name" in cols and "url" not in cols
        if is_legacy and not inspector.has_table("docs_legacy"):
            op.rename_table("docs", "docs_legacy")

    # 3) Create new docs table if missing
    if not inspector.has_table("docs"):
        op.create_table(
            "docs",
            sa.Column("id", sa.Integer(), sa.ForeignKey("resources.id"), primary_key=True),
            sa.Column("url", sa.String(length=2048), nullable=True),
            sa.Column("source", sa.String(length=200), nullable=True),
            sa.Column("category", sa.String(length=100), nullable=True),
            sa.Column("thumbnail_url", sa.String(length=1000), nullable=True),
        )
        op.create_index("ix_docs_url", "docs", ["url"], unique=True)

    # 4) Create articles table (joined-table)
    if not inspector.has_table("articles"):
        op.create_table(
            "articles",
            sa.Column("id", sa.Integer(), sa.ForeignKey("resources.id"), primary_key=True),
            sa.Column("url", sa.String(length=2048), nullable=False),
            sa.Column("source", sa.String(length=200), nullable=True),
            sa.Column("category", sa.String(length=100), nullable=True),
            sa.Column("thumbnail_url", sa.String(length=1000), nullable=True),
        )
        op.create_index("ix_articles_url", "articles", ["url"], unique=True)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if inspector.has_table("articles"):
        try:
            op.drop_index("ix_articles_url", table_name="articles")
        except Exception:
            pass
        op.drop_table("articles")

    if inspector.has_table("docs"):
        try:
            op.drop_index("ix_docs_url", table_name="docs")
        except Exception:
            pass
        op.drop_table("docs")

    # Restore legacy docs table name if present
    if inspector.has_table("docs_legacy") and not inspector.has_table("docs"):
        op.rename_table("docs_legacy", "docs")

    # Note: Postgres enum values cannot be removed safely in downgrade.
