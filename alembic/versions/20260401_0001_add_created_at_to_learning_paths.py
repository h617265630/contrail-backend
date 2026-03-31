"""add created_at to learning_paths

Revision ID: 20260401_0001
Revises:
Create Date: 2026-04-01

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260401_0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('learning_paths', sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.func.now()))


def downgrade() -> None:
    op.drop_column('learning_paths', 'created_at')
