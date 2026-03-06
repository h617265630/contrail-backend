"""
Add is_public column to user_resource table
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20260123_fix_add_is_public_to_user_resource'
down_revision = '20260122_0011_fix_resourcetype_enum_values'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('user_resource', sa.Column('is_public', sa.Boolean(), nullable=True))

def downgrade():
    op.drop_column('user_resource', 'is_public')
