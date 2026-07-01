"""add is_admin to users

Revision ID: 40b8fdf4a8f8
Revises: 79a58987b979
Create Date: 2026-07-01 00:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '40b8fdf4a8f8'
down_revision = 'e9f0f98fb534'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_admin', sa.Boolean(), nullable=False, server_default='false'))


def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('is_admin')
