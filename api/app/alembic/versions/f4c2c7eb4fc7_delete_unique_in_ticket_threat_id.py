"""delete-unique-in-ticket.threat_id

Revision ID: f4c2c7eb4fc7
Revises: f9986e152c5e
Create Date: 2025-04-14 04:18:06.093146

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f4c2c7eb4fc7'
down_revision = 'f9986e152c5e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_ticket_threat_id', table_name='ticket')
    op.create_index(op.f('ix_ticket_threat_id'), 'ticket', ['threat_id'], unique=False)
    op.alter_column('vuln', 'created_by',
               existing_type=sa.VARCHAR(length=36),
               nullable=True)
    op.drop_constraint('vuln_created_by_fkey', 'vuln', type_='foreignkey')
    op.create_foreign_key('vuln_created_by_fkey', 'vuln', 'account', ['created_by'], ['user_id'], ondelete='SET NULL')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('vuln_created_by_fkey', 'vuln', type_='foreignkey')
    op.create_foreign_key('vuln_created_by_fkey', 'vuln', 'account', ['created_by'], ['user_id'])
    op.alter_column('vuln', 'created_by',
               existing_type=sa.VARCHAR(length=36),
               nullable=False)
    op.drop_index(op.f('ix_ticket_threat_id'), table_name='ticket')
    op.create_index('ix_ticket_threat_id', 'ticket', ['threat_id'], unique=True)
    # ### end Alembic commands ###
