"""add type to learning_paths

Revision ID: 20260131_0001
Revises: 20260123_merge_heads
Create Date: 2026-01-31

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260131_0001'
down_revision = '20260123_merge_heads'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('learning_paths', sa.Column('type', sa.String(length=50), nullable=True))


def downgrade():
    op.drop_column('learning_paths', 'type')
