"""init

Revision ID: 9adb158bbcab
Revises: 
Create Date: 2021-11-19 12:27:03.446225

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '9adb158bbcab'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('job',
                    sa.Column('job_id', sa.String(length=64), nullable=False),
                    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'),
                              nullable=False),
                    sa.Column('updated_at', sa.DateTime(timezone=True),
                              server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False),
                    sa.Column('file_name', sa.String(length=255), nullable=False),
                    sa.Column('speaker', sa.String(length=255), nullable=False),
                    sa.Column('speed', sa.Float(), nullable=False),
                    sa.Column('state', sa.Enum('QUEUED', 'IN_PROGRESS', 'COMPLETED', 'EXPIRED', 'ERROR', name='state'),
                              nullable=False),
                    sa.Column('error_message', sa.String(length=255), nullable=True),
                    sa.PrimaryKeyConstraint('job_id')
                    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('job')
    # ### end Alembic commands ###
