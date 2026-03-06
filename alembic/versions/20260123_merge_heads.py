"""
Merge migration: unify multiple heads into one

Revision ID: 20260123_merge_heads
Revises: 20260123_0012,20260123_0013,20260123_update_resource_and_user_resource_public_fields
Create Date: 2026-01-23
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20260123_merge_heads'
down_revision = ('20260123_0012', '20260123_0013', '20260123_update_resource_and_user_resource_public_fields')
branch_labels = None
depends_on = None

def upgrade():
    pass  # 仅用于合并分支，无实际 schema 变更

def downgrade():
    pass
