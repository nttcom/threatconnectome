"""remove PTeamTagReference

Revision ID: c37e99fe5d4c
Revises: 522bad1d2d9c
Create Date: 2024-02-15 23:09:35.290995

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c37e99fe5d4c'
down_revision = '522bad1d2d9c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_pteamtagreference_group', table_name='pteamtagreference')
    op.drop_index('ix_pteamtagreference_pteam_id', table_name='pteamtagreference')
    op.drop_index('ix_pteamtagreference_tag_id', table_name='pteamtagreference')
    op.drop_table('pteamtagreference')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('pteamtagreference',
    sa.Column('reference_id', sa.VARCHAR(length=36), autoincrement=False, nullable=False),
    sa.Column('pteam_id', sa.VARCHAR(length=36), autoincrement=False, nullable=False),
    sa.Column('tag_id', sa.VARCHAR(length=36), autoincrement=False, nullable=False),
    sa.Column('group', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('target', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('version', sa.TEXT(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['pteam_id'], ['pteam.pteam_id'], name='pteamtagreference_pteam_id_fkey', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['tag_id'], ['tag.tag_id'], name='pteamtagreference_tag_id_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('reference_id', name='pteamtagreference_pkey'),
    sa.UniqueConstraint('pteam_id', 'tag_id', 'group', 'target', 'version', name='pteamtagreference_pteam_id_tag_id_group_target_version_key')
    )
    op.create_index('ix_pteamtagreference_tag_id', 'pteamtagreference', ['tag_id'], unique=False)
    op.create_index('ix_pteamtagreference_pteam_id', 'pteamtagreference', ['pteam_id'], unique=False)
    op.create_index('ix_pteamtagreference_group', 'pteamtagreference', ['group'], unique=False)
    # ### end Alembic commands ###
