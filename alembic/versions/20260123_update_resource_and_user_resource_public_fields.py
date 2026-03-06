"""
Update resource table: rename is_public to is_system_public (or add if missing)
Add is_public to user_resource table
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20260123_update_resource_and_user_resource_public_fields'
down_revision = '20260123_fix_add_is_public_to_user_resource'
branch_labels = None
depends_on = None

def upgrade():
    # 检查 resource 表是否有 is_public 字段
    conn = op.get_bind()
    insp = sa.inspect(conn)
    columns = [col['name'] for col in insp.get_columns('resources')]
    if 'is_public' in columns:
        op.alter_column('resources', 'is_public', new_column_name='is_system_public')
    elif 'is_system_public' not in columns:
        op.add_column('resources', sa.Column('is_system_public', sa.Boolean(), nullable=False, server_default=sa.text('false')))
    # user_resource 表添加 is_public 字段（如未添加）
    user_resource_columns = [col['name'] for col in insp.get_columns('user_resource')]
    if 'is_public' not in user_resource_columns:
        op.add_column('user_resource', sa.Column('is_public', sa.Boolean(), nullable=False, server_default=sa.text('false')))

def downgrade():
    # resource 表还原 is_system_public 字段
    conn = op.get_bind()
    insp = sa.inspect(conn)
    columns = [col['name'] for col in insp.get_columns('resources')]
    if 'is_system_public' in columns and 'is_public' not in columns:
        op.alter_column('resources', 'is_system_public', new_column_name='is_public')
    elif 'is_system_public' in columns:
        op.drop_column('resources', 'is_system_public')
    # user_resource 表移除 is_public 字段
    user_resource_columns = [col['name'] for col in insp.get_columns('user_resource')]
    if 'is_public' in user_resource_columns:
        op.drop_column('user_resource', 'is_public')
