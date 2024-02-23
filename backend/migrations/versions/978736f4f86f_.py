"""empty message

Revision ID: 978736f4f86f
Revises: 33a77965e153
Create Date: 2024-02-23 17:41:38.577546

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '978736f4f86f'
down_revision = '33a77965e153'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('follows')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('follows',
    sa.Column('following_user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('followed_user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['followed_user_id'], ['users.id'], name='follows_followed_user_id_fkey'),
    sa.ForeignKeyConstraint(['following_user_id'], ['users.id'], name='follows_following_user_id_fkey'),
    sa.PrimaryKeyConstraint('following_user_id', 'followed_user_id', name='follows_pkey')
    )
    # ### end Alembic commands ###