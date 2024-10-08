"""add service thumbnail and description

Revision ID: 734970d141c8
Revises: 4765ef6b26ef
Create Date: 2024-08-19 03:06:12.565426

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '734970d141c8'
down_revision = '4765ef6b26ef'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('servicethumbnail',
    sa.Column('service_id', sa.String(length=36), nullable=False),
    sa.Column('media_type', sa.String(length=255), nullable=False),
    sa.Column('image_data', sa.LargeBinary(), nullable=False),
    sa.ForeignKeyConstraint(['service_id'], ['service.service_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('service_id')
    )
    op.create_index(op.f('ix_servicethumbnail_service_id'), 'servicethumbnail', ['service_id'], unique=False)
    op.add_column('service', sa.Column('description', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('service', 'description')
    op.drop_index(op.f('ix_servicethumbnail_service_id'), table_name='servicethumbnail')
    op.drop_table('servicethumbnail')
    # ### end Alembic commands ###
