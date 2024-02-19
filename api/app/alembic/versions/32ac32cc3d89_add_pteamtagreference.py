"""add PTeamTagReference

Revision ID: 32ac32cc3d89
Revises: c37e99fe5d4c
Create Date: 2024-02-15 23:26:16.222682

"""

from typing import NamedTuple, Set

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '32ac32cc3d89'
down_revision = 'c37e99fe5d4c'
branch_labels = None
depends_on = None


def fill_pteam_tag_reference_table(new_reference_table: sa.sql.schema.Table) -> None:
    class RowData(NamedTuple):
        pteam_id: str
        tag_id: str
        group: str
        target: str
        version: str

    connection = op.get_bind()
    pteamtags = connection.exec_driver_sql("SELECT pteam_id, tag_id, refs FROM pteamtag").all()
    new_rows: Set[RowData] = set()
    for pteamtag in pteamtags:  # [pteam_id, tag_id, refs]
        pteam_id, tag_id, old_refs = pteamtag
        if not pteam_id or not tag_id:
            continue  # drop broken
        if not isinstance(old_refs, list):
            new_rows.add(RowData(pteam_id, tag_id, "", "", ""))  # maybe added by old UI
            continue
        for ref in old_refs:
            if not isinstance(ref, dict):
                new_rows.add(RowData(pteam_id, tag_id, "", "", ""))
                continue
            new_rows.add(
                RowData(
                    pteam_id,
                    tag_id,
                    ref.get("group", ""),
                    ref.get("target", ""),
                    ref.get("version", ""),
                )
            )
    op.bulk_insert(
        new_reference_table,
        [
            {
                "pteam_id": row.pteam_id,
                "tag_id": row.tag_id,
                "group": row.group,
                "target": row.target,
                "version": row.version,
            }
            for row in new_rows
        ],
    )


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    new_reference_table = op.create_table('pteamtagreference',
    sa.Column('pteam_id', sa.String(length=36), nullable=False),
    sa.Column('tag_id', sa.String(length=36), nullable=False),
    sa.Column('group', sa.String(length=255), nullable=False),
    sa.Column('target', sa.Text(), nullable=False),
    sa.Column('version', sa.Text(), nullable=False),
    sa.ForeignKeyConstraint(['pteam_id'], ['pteam.pteam_id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['tag_id'], ['tag.tag_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('pteam_id', 'tag_id', 'group', 'target', 'version')
    )
    op.create_index(op.f('ix_pteamtagreference_group'), 'pteamtagreference', ['group'], unique=False)
    op.create_index(op.f('ix_pteamtagreference_pteam_id'), 'pteamtagreference', ['pteam_id'], unique=False)
    op.create_index(op.f('ix_pteamtagreference_tag_id'), 'pteamtagreference', ['tag_id'], unique=False)

    fill_pteam_tag_reference_table(new_reference_table)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_pteamtagreference_tag_id'), table_name='pteamtagreference')
    op.drop_index(op.f('ix_pteamtagreference_pteam_id'), table_name='pteamtagreference')
    op.drop_index(op.f('ix_pteamtagreference_group'), table_name='pteamtagreference')
    op.drop_table('pteamtagreference')
    # ### end Alembic commands ###