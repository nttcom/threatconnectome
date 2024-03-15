"""obsolete gteam and badge

Revision ID: 47fd451d5c21
Revises: bea1dc749c90
Create Date: 2024-03-14 05:50:30.528376

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '47fd451d5c21'
down_revision = 'bea1dc749c90'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_gteamauthority_gteam_id', table_name='gteamauthority')
    op.drop_index('ix_gteamauthority_user_id', table_name='gteamauthority')
    op.drop_table('gteamauthority')
    op.drop_index('ix_account_favorite_badge', table_name='account')
    op.drop_constraint('account_favorite_badge_fkey', 'account', type_='foreignkey')
    op.drop_column('account', 'favorite_badge')
    op.drop_index('ix_secbadge_created_by', table_name='secbadge')
    op.drop_index('ix_secbadge_pteam_id', table_name='secbadge')
    op.drop_index('ix_secbadge_user_id', table_name='secbadge')
    op.drop_table('secbadge')
    op.drop_index('ix_topiczone_topic_id', table_name='topiczone')
    op.drop_index('ix_topiczone_zone_name', table_name='topiczone')
    op.drop_table('topiczone')
    op.drop_index('ix_actionzone_action_id', table_name='actionzone')
    op.drop_index('ix_actionzone_zone_name', table_name='actionzone')
    op.drop_table('actionzone')
    op.drop_index('ix_zone_created_by', table_name='zone')
    op.drop_index('ix_zone_gteam_id', table_name='zone')
    op.drop_index('ix_pteamzone_pteam_id', table_name='pteamzone')
    op.drop_index('ix_pteamzone_zone_name', table_name='pteamzone')
    op.drop_table('pteamzone')
    op.drop_table('zone')
    op.drop_index('ix_gteamaccount_gteam_id', table_name='gteamaccount')
    op.drop_index('ix_gteamaccount_user_id', table_name='gteamaccount')
    op.drop_table('gteamaccount')
    op.drop_index('ix_gteaminvitation_gteam_id', table_name='gteaminvitation')
    op.drop_index('ix_gteaminvitation_user_id', table_name='gteaminvitation')
    op.drop_table('gteaminvitation')
    op.drop_table('gteam')
    # drop auto generated Enums
    #   see https://github.com/sqlalchemy/alembic/issues/886
    sa.Enum(name="difficulty").drop(op.get_bind())
    sa.Enum(name="badgetype").drop(op.get_bind())
    sa.Enum(name="certifiertype").drop(op.get_bind())
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('account', sa.Column('favorite_badge', sa.VARCHAR(length=36), autoincrement=False, nullable=True))
    op.create_table('secbadge',
    sa.Column('badge_id', sa.VARCHAR(length=36), autoincrement=False, nullable=False),
    sa.Column('badge_name', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('image_url', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('user_id', sa.VARCHAR(length=36), autoincrement=False, nullable=False),
    sa.Column('email', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('created_by', sa.VARCHAR(length=36), autoincrement=False, nullable=False),
    sa.Column('obtained_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('expired_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('metadata_json', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=False),
    sa.Column('priority', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('difficulty', postgresql.ENUM('low', 'middle', 'high', name='difficulty'), autoincrement=False, nullable=False),
    sa.Column('badge_type', postgresql.ARRAY(postgresql.ENUM('skill', 'performance', 'position', name='badgetype')), autoincrement=False, nullable=False),
    sa.Column('certifier_type', postgresql.ENUM('trusted_third_party', 'coworker', 'myself', 'system', name='certifiertype'), autoincrement=False, nullable=False),
    sa.Column('pteam_id', sa.VARCHAR(length=36), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['created_by'], ['account.user_id'], name='secbadge_created_by_fkey'),
    sa.ForeignKeyConstraint(['pteam_id'], ['pteam.pteam_id'], name='secbadge_pteam_id_fkey'),
    sa.ForeignKeyConstraint(['user_id'], ['account.user_id'], name='secbadge_user_id_fkey'),
    sa.PrimaryKeyConstraint('badge_id', name='secbadge_pkey'),
    postgresql_ignore_search_path=False
    )
    op.create_index('ix_secbadge_user_id', 'secbadge', ['user_id'], unique=False)
    op.create_index('ix_secbadge_pteam_id', 'secbadge', ['pteam_id'], unique=False)
    op.create_index('ix_secbadge_created_by', 'secbadge', ['created_by'], unique=False)
    op.create_foreign_key('account_favorite_badge_fkey', 'account', 'secbadge', ['favorite_badge'], ['badge_id'])
    op.create_index('ix_account_favorite_badge', 'account', ['favorite_badge'], unique=False)
    op.create_table('gteam',
    sa.Column('gteam_id', sa.VARCHAR(length=36), autoincrement=False, nullable=False),
    sa.Column('gteam_name', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('contact_info', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('gteam_id', name='gteam_pkey'),
    postgresql_ignore_search_path=False
    )
    op.create_table('zone',
    sa.Column('zone_name', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('zone_info', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('gteam_id', sa.VARCHAR(length=36), autoincrement=False, nullable=False),
    sa.Column('created_by', sa.VARCHAR(length=36), autoincrement=False, nullable=False),
    sa.Column('archived', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['created_by'], ['account.user_id'], name='zone_created_by_fkey'),
    sa.ForeignKeyConstraint(['gteam_id'], ['gteam.gteam_id'], name='zone_gteam_id_fkey'),
    sa.PrimaryKeyConstraint('zone_name', name='zone_pkey'),
    postgresql_ignore_search_path=False
    )
    op.create_index('ix_zone_gteam_id', 'zone', ['gteam_id'], unique=False)
    op.create_index('ix_zone_created_by', 'zone', ['created_by'], unique=False)
    op.create_table('actionzone',
    sa.Column('action_id', sa.VARCHAR(length=36), autoincrement=False, nullable=False),
    sa.Column('zone_name', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['action_id'], ['topicaction.action_id'], name='actionzone_action_id_fkey'),
    sa.ForeignKeyConstraint(['zone_name'], ['zone.zone_name'], name='actionzone_zone_name_fkey'),
    sa.PrimaryKeyConstraint('action_id', 'zone_name', name='actionzone_pkey')
    )
    op.create_index('ix_actionzone_zone_name', 'actionzone', ['zone_name'], unique=False)
    op.create_index('ix_actionzone_action_id', 'actionzone', ['action_id'], unique=False)
    op.create_table('gteaminvitation',
    sa.Column('invitation_id', sa.VARCHAR(length=36), autoincrement=False, nullable=False),
    sa.Column('gteam_id', sa.VARCHAR(length=36), autoincrement=False, nullable=False),
    sa.Column('user_id', sa.VARCHAR(length=36), autoincrement=False, nullable=False),
    sa.Column('expiration', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('limit_count', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('used_count', sa.INTEGER(), server_default=sa.text('0'), autoincrement=False, nullable=False),
    sa.Column('authority', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['gteam_id'], ['gteam.gteam_id'], name='gteaminvitation_gteam_id_fkey'),
    sa.ForeignKeyConstraint(['user_id'], ['account.user_id'], name='gteaminvitation_user_id_fkey'),
    sa.PrimaryKeyConstraint('invitation_id', name='gteaminvitation_pkey')
    )
    op.create_index('ix_gteaminvitation_user_id', 'gteaminvitation', ['user_id'], unique=False)
    op.create_index('ix_gteaminvitation_gteam_id', 'gteaminvitation', ['gteam_id'], unique=False)
    op.create_table('pteamzone',
    sa.Column('pteam_id', sa.VARCHAR(length=36), autoincrement=False, nullable=False),
    sa.Column('zone_name', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['pteam_id'], ['pteam.pteam_id'], name='pteamzone_pteam_id_fkey'),
    sa.ForeignKeyConstraint(['zone_name'], ['zone.zone_name'], name='pteamzone_zone_name_fkey'),
    sa.PrimaryKeyConstraint('pteam_id', 'zone_name', name='pteamzone_pkey')
    )
    op.create_index('ix_pteamzone_zone_name', 'pteamzone', ['zone_name'], unique=False)
    op.create_index('ix_pteamzone_pteam_id', 'pteamzone', ['pteam_id'], unique=False)
    op.create_table('gteamaccount',
    sa.Column('gteam_id', sa.VARCHAR(length=36), autoincrement=False, nullable=False),
    sa.Column('user_id', sa.VARCHAR(length=36), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['gteam_id'], ['gteam.gteam_id'], name='gteamaccount_gteam_id_fkey'),
    sa.ForeignKeyConstraint(['user_id'], ['account.user_id'], name='gteamaccount_user_id_fkey'),
    sa.PrimaryKeyConstraint('gteam_id', 'user_id', name='gteamaccount_pkey')
    )
    op.create_index('ix_gteamaccount_user_id', 'gteamaccount', ['user_id'], unique=False)
    op.create_index('ix_gteamaccount_gteam_id', 'gteamaccount', ['gteam_id'], unique=False)
    op.create_table('topiczone',
    sa.Column('topic_id', sa.VARCHAR(length=36), autoincrement=False, nullable=False),
    sa.Column('zone_name', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['topic_id'], ['topic.topic_id'], name='topiczone_topic_id_fkey', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['zone_name'], ['zone.zone_name'], name='topiczone_zone_name_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('topic_id', 'zone_name', name='topiczone_pkey')
    )
    op.create_index('ix_topiczone_zone_name', 'topiczone', ['zone_name'], unique=False)
    op.create_index('ix_topiczone_topic_id', 'topiczone', ['topic_id'], unique=False)
    op.create_table('gteamauthority',
    sa.Column('gteam_id', sa.VARCHAR(length=36), autoincrement=False, nullable=False),
    sa.Column('user_id', sa.VARCHAR(length=36), autoincrement=False, nullable=False),
    sa.Column('authority', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['gteam_id'], ['gteam.gteam_id'], name='gteamauthority_gteam_id_fkey'),
    sa.ForeignKeyConstraint(['user_id'], ['account.user_id'], name='gteamauthority_user_id_fkey'),
    sa.PrimaryKeyConstraint('gteam_id', 'user_id', name='gteamauthority_pkey')
    )
    op.create_index('ix_gteamauthority_user_id', 'gteamauthority', ['user_id'], unique=False)
    op.create_index('ix_gteamauthority_gteam_id', 'gteamauthority', ['gteam_id'], unique=False)
    # ### end Alembic commands ###
