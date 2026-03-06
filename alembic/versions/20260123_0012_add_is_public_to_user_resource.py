"""add is_public to user_resource table

Revision ID: 20260123_0012
Revises: 20260122_0011_fix_resourcetype_enum_values
Create Date: 2026-01-23

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260123_0012"
down_revision = "20260122_0011_fix_resourcetype_enum_values"
branch_labels = None
depends_on = None


def _has_column(inspector: sa.Inspector, table: str, column: str) -> bool:
    return any(c["name"] == column for c in inspector.get_columns(table))


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # Add is_public column to user_resource table if it doesn't exist
    if inspector.has_table("user_resource"):
        with op.batch_alter_table("user_resource") as batch_op:
            if not _has_column(inspector, "user_resource", "is_public"):
                batch_op.add_column(
                    sa.Column(
                        "is_public",
                        sa.Boolean(),
                        nullable=False,
                        server_default=sa.false(),
                    )
                )

        # Drop server default to keep model-level default as the main source of truth
        with op.batch_alter_table("user_resource") as batch_op:
            batch_op.alter_column("is_public", server_default=None)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if inspector.has_table("user_resource") and _has_column(inspector, "user_resource", "is_public"):
        with op.batch_alter_table("user_resource") as batch_op:
            batch_op.drop_column("is_public")