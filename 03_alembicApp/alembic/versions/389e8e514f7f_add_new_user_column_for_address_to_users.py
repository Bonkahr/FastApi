"""add new user column for address to users

Revision ID: 389e8e514f7f
Revises: ba74e0c26c50
Create Date: 2023-06-21 16:59:33.328694

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '389e8e514f7f'
down_revision = 'ba74e0c26c50'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column('address_id', sa.Integer(), nullable=True))
    op.create_foreign_key('address_users_fk', source_table='users',
                          referent_table='address', local_cols=['address_id'],
                          remote_cols=['id'], ondelete='CASCADE')


def downgrade() -> None:
    op.drop_constraint('address_users_fk', table_name='users')
    op.drop_column('users', 'address_id')
