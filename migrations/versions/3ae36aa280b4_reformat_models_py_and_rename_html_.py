"""reformat models.py and rename html_color_class

Revision ID: 3ae36aa280b4
Revises: c9f6566b30be
Create Date: 2024-07-22 22:55:46.118518

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '3ae36aa280b4'
down_revision = 'c9f6566b30be'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('blogpage', schema=None) as batch_op:
        batch_op.add_column(sa.Column('html_color_class', sa.String(length=100), nullable=True))
        batch_op.drop_column('color_html_class')

    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.alter_column('content',
               existing_type=mysql.MEDIUMTEXT(charset='utf8mb3', collation='utf8mb3_bin'),
               type_=sa.Text(length=100000),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.alter_column('content',
               existing_type=sa.Text(length=100000),
               type_=mysql.MEDIUMTEXT(charset='utf8mb3', collation='utf8mb3_bin'),
               nullable=False)

    with op.batch_alter_table('blogpage', schema=None) as batch_op:
        batch_op.add_column(sa.Column('color_html_class', mysql.VARCHAR(length=100), nullable=True))
        batch_op.drop_column('html_color_class')

    # ### end Alembic commands ###
