"""ensure resourcetype enum contains required values

Revision ID: 20260122_0011
Revises: 20260122_0010
Create Date: 2026-01-22

"""

from __future__ import annotations

from alembic import op


revision = "20260122_0011_fix_resourcetype_enum_values"
down_revision = "20260122_0010"
branch_labels = None
depends_on = None


def _add_enum_value(enum_name: str, value: str) -> None:
    # Postgres enum values are case-sensitive.
    # We can't safely remove values in downgrade; only add if missing.
    op.execute(
        f"""
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM pg_enum e
    JOIN pg_type t ON t.oid = e.enumtypid
    WHERE t.typname = '{enum_name}' AND e.enumlabel = '{value}'
  ) THEN
    ALTER TYPE {enum_name} ADD VALUE '{value}';
  END IF;
END$$;
"""
    )


def upgrade() -> None:
    # Make sure required resource types exist in DB enum
    for val in ("video", "document", "article", "link", "clip"):
        try:
            _add_enum_value("resourcetype", val)
        except Exception:
            # best-effort: ignore DBs that don't support enums or when type doesn't exist
            pass


def downgrade() -> None:
    # Postgres enums can't drop values safely.
    pass
