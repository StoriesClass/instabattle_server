"""empty message

Revision ID: c60d3b7a161a
Revises: e9ec73f11c2b
Create Date: 2016-12-18 18:37:06.121151

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c60d3b7a161a'
down_revision = 'e9ec73f11c2b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('votes', schema=None) as batch_op:
        batch_op.add_column(sa.Column('loser_id', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('winner_id', sa.Integer(), nullable=False))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key(None, 'entries', ['winner_id'], ['id'])
        batch_op.create_foreign_key(None, 'entries', ['loser_id'], ['id'])
        batch_op.drop_column('chosen_entry')
        batch_op.drop_column('entry_left_id')
        batch_op.drop_column('entry_right_id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('votes', schema=None) as batch_op:
        batch_op.add_column(sa.Column('entry_right_id', sa.INTEGER(), nullable=False))
        batch_op.add_column(sa.Column('entry_left_id', sa.INTEGER(), nullable=False))
        batch_op.add_column(sa.Column('chosen_entry', sa.VARCHAR(length=5), nullable=True))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key(None, 'entries', ['entry_right_id'], ['id'])
        batch_op.create_foreign_key(None, 'entries', ['entry_left_id'], ['id'])
        batch_op.drop_column('winner_id')
        batch_op.drop_column('loser_id')

    # ### end Alembic commands ###
