"""Added current time to bet data

Revision ID: 5251bb552eb7
Revises: 17724f5cc1c2
Create Date: 2014-12-14 10:59:47.994484

"""

# revision identifiers, used by Alembic.
revision = '5251bb552eb7'
down_revision = '17724f5cc1c2'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('bet_match', sa.Column('current_date_time', sa.DateTime(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('bet_match', 'current_date_time')
    ### end Alembic commands ###