"""empty message

Revision ID: 5621e5866453
Revises: 75c77be7631e
Create Date: 2022-06-15 23:15:04.487392

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5621e5866453'
down_revision = '75c77be7631e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('route', sa.Column('plane', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'route', 'aircraft', ['plane'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'route', type_='foreignkey')
    op.drop_column('route', 'plane')
    # ### end Alembic commands ###
