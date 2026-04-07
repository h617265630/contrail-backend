"""Make category name/code unique per owner (not globally)

Revision ID: 20260407_0001
Revises: 20260330_0001
Create Date: 2026-04-07

Changes:
- Remove global UNIQUE constraints on categories.name and categories.code
- Add partial unique indexes:
  - System categories (owner_user_id IS NULL): name and code must still be globally unique
  - User categories: (name, owner_user_id) and (code, owner_user_id) are unique
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260407_0001"
down_revision: Union[str, Sequence[str], None] = "20260330_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()

    # 1. Drop the global unique constraints if they exist
    for constraint_name in ("categories_name_key", "categories_code_key"):
        try:
            op.execute(f"ALTER TABLE categories DROP CONSTRAINT IF EXISTS {constraint_name}")
        except Exception:
            pass  # Constraint may not exist in all environments

    # 2. Add partial unique index for system categories (owner_user_id IS NULL)
    # Using a partial index so NULL owner rows can't have duplicate names/codes
    op.execute(
        """
        CREATE UNIQUE INDEX uq_category_name_system
        ON categories (name)
        WHERE owner_user_id IS NULL
        """
    )
    op.execute(
        """
        CREATE UNIQUE INDEX uq_category_code_system
        ON categories (code)
        WHERE owner_user_id IS NULL
        """
    )

    # 3. Add unique constraint for user categories (owner_user_id IS NOT NULL)
    # PostgreSQL treats NULLs as distinct, so multiple NULL owners won't conflict
    op.execute(
        """
        CREATE UNIQUE INDEX uq_category_name_user
        ON categories (name, owner_user_id)
        WHERE owner_user_id IS NOT NULL
        """
    )
    op.execute(
        """
        CREATE UNIQUE INDEX uq_category_code_user
        ON categories (code, owner_user_id)
        WHERE owner_user_id IS NOT NULL
        """
    )


def downgrade() -> None:
    # Drop the partial indexes
    op.execute("DROP INDEX IF EXISTS uq_category_name_system")
    op.execute("DROP INDEX IF EXISTS uq_category_code_system")
    op.execute("DROP INDEX IF EXISTS uq_category_name_user")
    op.execute("DROP INDEX IF EXISTS uq_category_code_user")

    # Re-add global unique constraints (SQLite-compatible via a plain ALTER)
    # Note: This uses a DB-agnostic approach. In production PostgreSQL,
    # use proper named constraints.
    try:
        op.execute(
            "ALTER TABLE categories ADD CONSTRAINT categories_name_key UNIQUE (name)"
        )
        op.execute(
            "ALTER TABLE categories ADD CONSTRAINT categories_code_key UNIQUE (code)"
        )
    except Exception:
        pass  # May fail if constraints already exist
