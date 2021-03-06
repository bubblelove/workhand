"""initial migration

Revision ID: b935cf54e49c
Revises: None
Create Date: 2016-03-20 21:21:48.440900

"""

# revision identifiers, used by Alembic.
revision = 'b935cf54e49c'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('last_seen', sa.DateTime(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'last_seen')
    ### end Alembic commands ###
