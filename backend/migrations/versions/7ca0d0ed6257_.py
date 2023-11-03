"""empty message

Revision ID: 7ca0d0ed6257
Revises: 
Create Date: 2023-11-03 22:47:56.194823

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7ca0d0ed6257'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('recipes', schema=None) as batch_op:
        batch_op.add_column(sa.Column('prepare_time', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('cook_time', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('image', sa.LargeBinary(), nullable=True))

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('image', sa.LargeBinary(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('image')

    with op.batch_alter_table('recipes', schema=None) as batch_op:
        batch_op.drop_column('image')
        batch_op.drop_column('cook_time')
        batch_op.drop_column('prepare_time')

    # ### end Alembic commands ###
