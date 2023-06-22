"""create address table

Revision ID: ba74e0c26c50
Revises: 7fe973dde62d
Create Date: 2023-06-21 16:50:43.021832

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ba74e0c26c50'
down_revision = '7fe973dde62d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('address',
                    sa.Column('id', sa.Integer(), nullable=False,
                              primary_key=True),
                    sa.Column('address_1', sa.String(), nullable=False),
                    sa.Column('address_2', sa.String(), nullable=False),
                    sa.Column('city', sa.String(), nullable=False),
                    sa.Column('state', sa.String(), nullable=False),
                    sa.Column('country', sa.String(), nullable=False),
                    sa.Column('postal_code', sa.String(), nullable=False)
                    )


def downgrade() -> None:
    op.drop_table('address')
