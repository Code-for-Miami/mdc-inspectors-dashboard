"""empty message

Revision ID: 2ae65caa2c99
Revises: e19a9fd3ec5
Create Date: 2015-11-17 12:31:49.076442

"""

# revision identifiers, used by Alembic.
revision = '2ae65caa2c99'
down_revision = 'e19a9fd3ec5'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('monthly-report',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email_list', sa.String(length=200), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_monthly-report_id'), 'monthly-report', ['id'], unique=False)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_monthly-report_id'), table_name='monthly-report')
    op.drop_table('monthly-report')
    ### end Alembic commands ###