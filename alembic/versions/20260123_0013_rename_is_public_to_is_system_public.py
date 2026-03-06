"""rename is_public to is_system_public in resources table

Revision ID: 20260123_0013
Revises: 20260122_0011_fix_resourcetype_enum_values
Create Date: 2026-01-23

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260123_0013"
down_revision = "20260122_0011_fix_resourcetype_enum_values"
branch_labels = None
depends_on = None


def _has_column(inspector: sa.Inspector, table: str, column: str) -> bool:
    return any(c["name"] == column for c in inspector.get_columns(table))


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if inspector.has_table("resources"):
        # Check if is_public column exists and is_system_public doesn't exist
        has_is_public = _has_column(inspector, "resources", "is_public")
        has_is_system_public = _has_column(inspector, "resources", "is_system_public")
        
        if has_is_public and not has_is_system_public:
            # Rename is_public to is_system_public
            with op.batch_alter_table("resources") as batch_op:
                batch_op.alter_column("is_public", new_column_name="is_system_public")


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if inspector.has_table("resources"):
        has_is_system_public = _has_column(inspector, "resources", "is_system_public")
        has_is_public = _has_column(inspector, "resources", "is_public")
        
        if has_is_system_public and not has_is_public:
            # Rename is_system_public back to is_public
            with op.batch_alter_table("resources") as batch_op:
                batch_op.alter_column("is_system_public", new_column_name="is_public")