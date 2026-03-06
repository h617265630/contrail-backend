"""
Add is_system column to categories table
Revision ID: 20260122_0006
Revises: 29e742b2dd9f
Create Date: 2026-01-22
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20260122_0006'
down_revision = '29e742b2dd9f'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('categories', sa.Column('is_system', sa.Boolean(), server_default=sa.text('false')))

def downgrade():
    op.drop_column('categories', 'is_system')