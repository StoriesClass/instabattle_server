"""empty message

Revision ID: e9ec73f11c2b
Revises: e4109efc6113
Create Date: 2016-12-18 17:14:23.528094

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e9ec73f11c2b'
down_revision = 'e4109efc6113'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('battles', schema=None) as batch_op:
        batch_op.add_column(sa.Column('radius', sa.Integer(), server_default="100", nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('battles', schema=None) as batch_op:
        batch_op.drop_column('radius')

    # ### end Alembic commands ###