"""empty message

Revision ID: d4c1ef7b1a81
Revises: 91dd91a31125
Create Date: 2024-02-05 12:16:28.141904

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd4c1ef7b1a81'
down_revision = '91dd91a31125'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('ingrediants', schema=None) as batch_op:
        batch_op.add_column(sa.Column('item_number', sa.Integer(), nullable=False))
        batch_op.drop_column('id')

    with op.batch_alter_table('instructions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('step_number', sa.Integer(), nullable=False))
        batch_op.drop_column('id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('instructions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('id', sa.INTEGER(), autoincrement=False, nullable=False))
        batch_op.drop_column('step_number')

    with op.batch_alter_table('ingrediants', schema=None) as batch_op:
        batch_op.add_column(sa.Column('id', sa.INTEGER(), autoincrement=False, nullable=False))
        batch_op.drop_column('item_number')

    # ### end Alembic commands ###
