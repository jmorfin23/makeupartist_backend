"""empty message

Revision ID: 327d7e98c5ae
Revises: 
Create Date: 2020-09-14 18:17:39.856168

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '327d7e98c5ae'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('blog_post',
    sa.Column('blog_post_id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=150), nullable=True),
    sa.Column('author', sa.String(length=60), nullable=True),
    sa.Column('url', sa.String(length=250), nullable=True),
    sa.Column('path', sa.String(length=150), nullable=True),
    sa.Column('content', sa.Text(), nullable=True),
    sa.Column('date_posted', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('blog_post_id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)
    op.create_table('comment',
    sa.Column('comment_id', sa.Integer(), nullable=False),
    sa.Column('blog_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('message', sa.String(length=250), nullable=True),
    sa.Column('date_posted', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['blog_id'], ['blog_post.blog_post_id'], ),
    sa.PrimaryKeyConstraint('comment_id')
    )
    op.create_table('image_post',
    sa.Column('post_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('type', sa.String(length=50), nullable=True),
    sa.Column('url', sa.String(length=250), nullable=True),
    sa.Column('date_posted', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('post_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('image_post')
    op.drop_table('comment')
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_table('user')
    op.drop_table('blog_post')
    # ### end Alembic commands ###
