"""add user_images table

Revision ID: 20260131_0002
Revises: 20260131_0001
Create Date: 2026-01-31

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260131_0002'
down_revision = '20260131_0001'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table('user_images'):
        op.create_table(
            'user_images',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
            sa.Column('title', sa.String(length=200), nullable=True),
            sa.Column('image_url', sa.String(length=2048), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=True),
        )

    existing_indexes = {ix.get('name') for ix in inspector.get_indexes('user_images')} if inspector.has_table('user_images') else set()
    if 'ix_user_images_id' not in existing_indexes:
        op.create_index('ix_user_images_id', 'user_images', ['id'])
    if 'ix_user_images_user_id' not in existing_indexes:
        op.create_index('ix_user_images_user_id', 'user_images', ['user_id'])


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table('user_images'):
        return

    try:
        op.drop_index('ix_user_images_user_id', table_name='user_images')
    except Exception:
        pass
    try:
        op.drop_index('ix_user_images_id', table_name='user_images')
    except Exception:
        pass
    op.drop_table('user_images')
