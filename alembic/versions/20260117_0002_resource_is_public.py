"""add is_public to resources

Revision ID: 20260117_0002
Revises: 20260111_0001
Create Date: 2026-01-17

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260117_0002"
down_revision = "20260111_0001"
branch_labels = None
depends_on = None


def _has_column(inspector: sa.Inspector, table: str, column: str) -> bool:
    return any(c["name"] == column for c in inspector.get_columns(table))


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if inspector.has_table("resources"):
        with op.batch_alter_table("resources") as batch:
            if not _has_column(inspector, "resources", "is_public"):
                batch.add_column(
                    sa.Column(
                        "is_public",
                        sa.Boolean(),
                        nullable=False,
                        server_default=sa.true(),
                    )
                )

        # drop server default to keep model-level default as the main source of truth
        with op.batch_alter_table("resources") as batch:
            batch.alter_column("is_public", server_default=None)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if inspector.has_table("resources"):
        with op.batch_alter_table("resources") as batch:
            if _has_column(inspector, "resources", "is_public"):
                batch.drop_column("is_public")
