"""Initial

Revision ID: 38cbbe8bb594
Revises: 
Create Date: 2023-10-03 00:46:58.514638

"""
from alembic import op
from os import environ
from uuid import UUID
import sqlalchemy as sa

# copy constants from constants.py instead of import
MEMBER_UUID: UUID = UUID(int=0xCAFE0001)
NOT_MEMBER_UUID: UUID = UUID(int=0xCAFE0002)
SYSTEM_UUID: UUID = UUID(int=0xCAFE0011)
SYSTEM_EMAIL: str = environ.get("SYSTEM_EMAIL") or "SYSTEM_ACCOUNT"

# revision identifiers, used by Alembic.
revision = '38cbbe8bb594'
down_revision = None
branch_labels = None
depends_on = None


def insert_threatconnectome_system_accounts(account_table) -> None:
    op.bulk_insert(
        account_table,
        [
            # Note:
            #   All entries should have *same keys*, otherwise some column can be ignored.
            #   Entries below will make SQL: 'INSERT INTO account ("user_id", uid, email, disabled)
            #   VALUES (...), (...), (...)' based on the first entry. If only the 3rd entry has
            #   a key "years", it will be ignored (because the first entry does not have "years").
            {
                "user_id": str(MEMBER_UUID),
                "uid": "(pseudo account: pteam member)",
                "email": None,
                "disabled": True,
            },
            {
                "user_id": str(NOT_MEMBER_UUID),
                "uid": "(pseudo account: not pteam member)",
                "email": None,
                "disabled": True,
            },
            {
                "user_id": str(SYSTEM_UUID),
                "uid": "(pseudo account: system)",
                "email": SYSTEM_EMAIL,
                "disabled": True,
            },
        ],
    )


def upgrade() -> None:
    account_table = op.create_table('account',
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('uid', sa.Text(), nullable=True),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('disabled', sa.Boolean(), nullable=False),
    sa.Column('years', sa.Integer(), nullable=True),
    sa.Column('favorite_badge', sa.String(length=36), nullable=True),
    sa.ForeignKeyConstraint(['favorite_badge'], ['secbadge.badge_id'], use_alter=True),
    sa.PrimaryKeyConstraint('user_id'),
    sa.UniqueConstraint('uid')
    )
    op.create_index(op.f('ix_account_favorite_badge'), 'account', ['favorite_badge'], unique=False)
    op.create_table('ateam',
    sa.Column('ateam_id', sa.String(length=36), nullable=False),
    sa.Column('ateam_name', sa.String(length=255), nullable=False),
    sa.Column('contact_info', sa.String(length=255), nullable=False),
    sa.Column('slack_webhook_url', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('ateam_id')
    )
    op.create_table('gteam',
    sa.Column('gteam_id', sa.String(length=36), nullable=False),
    sa.Column('gteam_name', sa.String(length=255), nullable=False),
    sa.Column('contact_info', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('gteam_id')
    )
    op.create_table('misptag',
    sa.Column('tag_id', sa.String(length=36), nullable=False),
    sa.Column('tag_name', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('tag_id')
    )
    op.create_table('pteam',
    sa.Column('pteam_id', sa.String(length=36), nullable=False),
    sa.Column('pteam_name', sa.String(length=255), nullable=False),
    sa.Column('contact_info', sa.String(length=255), nullable=False),
    sa.Column('slack_webhook_url', sa.String(length=255), nullable=False),
    sa.Column('alert_threat_impact', sa.Integer(), nullable=True),
    sa.Column('disabled', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('pteam_id')
    )
    op.create_table('tag',
    sa.Column('tag_id', sa.String(length=36), nullable=False),
    sa.Column('tag_name', sa.Text(), nullable=False),
    sa.Column('parent_id', sa.String(length=36), nullable=True),
    sa.Column('parent_name', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['parent_id'], ['tag.tag_id'], ),
    sa.ForeignKeyConstraint(['parent_name'], ['tag.tag_name'], ),
    sa.PrimaryKeyConstraint('tag_id'),
    sa.UniqueConstraint('tag_name')
    )
    op.create_index(op.f('ix_tag_parent_id'), 'tag', ['parent_id'], unique=False)
    op.create_index(op.f('ix_tag_parent_name'), 'tag', ['parent_name'], unique=False)
    op.create_table('actionlog',
    sa.Column('logging_id', sa.String(length=36), nullable=False),
    sa.Column('action_id', sa.String(length=36), nullable=False),
    sa.Column('topic_id', sa.String(length=36), nullable=False),
    sa.Column('action', sa.Text(), nullable=False),
    sa.Column('action_type', sa.Enum('elimination', 'transfer', 'mitigation', 'acceptance', 'detection', 'rejection', name='actiontype'), nullable=False),
    sa.Column('recommended', sa.Boolean(), nullable=False),
    sa.Column('user_id', sa.String(length=36), nullable=True),
    sa.Column('pteam_id', sa.String(length=36), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('executed_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.ForeignKeyConstraint(['pteam_id'], ['pteam.pteam_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['account.user_id'], ),
    sa.PrimaryKeyConstraint('logging_id')
    )
    op.create_index(op.f('ix_actionlog_pteam_id'), 'actionlog', ['pteam_id'], unique=False)
    op.create_index(op.f('ix_actionlog_user_id'), 'actionlog', ['user_id'], unique=False)
    op.create_table('ateamaccount',
    sa.Column('ateam_id', sa.String(length=36), nullable=False),
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.ForeignKeyConstraint(['ateam_id'], ['ateam.ateam_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['account.user_id'], ),
    sa.PrimaryKeyConstraint('ateam_id', 'user_id')
    )
    op.create_index(op.f('ix_ateamaccount_ateam_id'), 'ateamaccount', ['ateam_id'], unique=False)
    op.create_index(op.f('ix_ateamaccount_user_id'), 'ateamaccount', ['user_id'], unique=False)
    op.create_table('ateamauthority',
    sa.Column('ateam_id', sa.String(length=36), nullable=False),
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('authority', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['ateam_id'], ['ateam.ateam_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['account.user_id'], ),
    sa.PrimaryKeyConstraint('ateam_id', 'user_id')
    )
    op.create_index(op.f('ix_ateamauthority_ateam_id'), 'ateamauthority', ['ateam_id'], unique=False)
    op.create_index(op.f('ix_ateamauthority_user_id'), 'ateamauthority', ['user_id'], unique=False)
    op.create_table('ateaminvitation',
    sa.Column('invitation_id', sa.String(length=36), nullable=False),
    sa.Column('ateam_id', sa.String(length=36), nullable=False),
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('expiration', sa.DateTime(), nullable=False),
    sa.Column('limit_count', sa.Integer(), nullable=True),
    sa.Column('used_count', sa.Integer(), server_default='0', nullable=False),
    sa.Column('authority', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['ateam_id'], ['ateam.ateam_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['account.user_id'], ),
    sa.PrimaryKeyConstraint('invitation_id')
    )
    op.create_index(op.f('ix_ateaminvitation_ateam_id'), 'ateaminvitation', ['ateam_id'], unique=False)
    op.create_index(op.f('ix_ateaminvitation_user_id'), 'ateaminvitation', ['user_id'], unique=False)
    op.create_table('ateampteam',
    sa.Column('ateam_id', sa.String(length=36), nullable=False),
    sa.Column('pteam_id', sa.String(length=36), nullable=False),
    sa.ForeignKeyConstraint(['ateam_id'], ['ateam.ateam_id'], ),
    sa.ForeignKeyConstraint(['pteam_id'], ['pteam.pteam_id'], ),
    sa.PrimaryKeyConstraint('ateam_id', 'pteam_id')
    )
    op.create_index(op.f('ix_ateampteam_ateam_id'), 'ateampteam', ['ateam_id'], unique=False)
    op.create_index(op.f('ix_ateampteam_pteam_id'), 'ateampteam', ['pteam_id'], unique=False)
    op.create_table('ateamwatchingrequest',
    sa.Column('request_id', sa.String(length=36), nullable=False),
    sa.Column('ateam_id', sa.String(length=36), nullable=False),
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('expiration', sa.DateTime(), nullable=False),
    sa.Column('limit_count', sa.Integer(), nullable=True),
    sa.Column('used_count', sa.Integer(), server_default='0', nullable=False),
    sa.ForeignKeyConstraint(['ateam_id'], ['ateam.ateam_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['account.user_id'], ),
    sa.PrimaryKeyConstraint('request_id')
    )
    op.create_index(op.f('ix_ateamwatchingrequest_ateam_id'), 'ateamwatchingrequest', ['ateam_id'], unique=False)
    op.create_index(op.f('ix_ateamwatchingrequest_user_id'), 'ateamwatchingrequest', ['user_id'], unique=False)
    op.create_table('gteamaccount',
    sa.Column('gteam_id', sa.String(length=36), nullable=False),
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.ForeignKeyConstraint(['gteam_id'], ['gteam.gteam_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['account.user_id'], ),
    sa.PrimaryKeyConstraint('gteam_id', 'user_id')
    )
    op.create_index(op.f('ix_gteamaccount_gteam_id'), 'gteamaccount', ['gteam_id'], unique=False)
    op.create_index(op.f('ix_gteamaccount_user_id'), 'gteamaccount', ['user_id'], unique=False)
    op.create_table('gteamauthority',
    sa.Column('gteam_id', sa.String(length=36), nullable=False),
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('authority', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['gteam_id'], ['gteam.gteam_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['account.user_id'], ),
    sa.PrimaryKeyConstraint('gteam_id', 'user_id')
    )
    op.create_index(op.f('ix_gteamauthority_gteam_id'), 'gteamauthority', ['gteam_id'], unique=False)
    op.create_index(op.f('ix_gteamauthority_user_id'), 'gteamauthority', ['user_id'], unique=False)
    op.create_table('gteaminvitation',
    sa.Column('invitation_id', sa.String(length=36), nullable=False),
    sa.Column('gteam_id', sa.String(length=36), nullable=False),
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('expiration', sa.DateTime(), nullable=False),
    sa.Column('limit_count', sa.Integer(), nullable=True),
    sa.Column('used_count', sa.Integer(), server_default='0', nullable=False),
    sa.Column('authority', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['gteam_id'], ['gteam.gteam_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['account.user_id'], ),
    sa.PrimaryKeyConstraint('invitation_id')
    )
    op.create_index(op.f('ix_gteaminvitation_gteam_id'), 'gteaminvitation', ['gteam_id'], unique=False)
    op.create_index(op.f('ix_gteaminvitation_user_id'), 'gteaminvitation', ['user_id'], unique=False)
    op.create_table('pteamaccount',
    sa.Column('pteam_id', sa.String(length=36), nullable=False),
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.ForeignKeyConstraint(['pteam_id'], ['pteam.pteam_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['account.user_id'], ),
    sa.PrimaryKeyConstraint('pteam_id', 'user_id')
    )
    op.create_index(op.f('ix_pteamaccount_pteam_id'), 'pteamaccount', ['pteam_id'], unique=False)
    op.create_index(op.f('ix_pteamaccount_user_id'), 'pteamaccount', ['user_id'], unique=False)
    op.create_table('pteamauthority',
    sa.Column('pteam_id', sa.String(length=36), nullable=False),
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('authority', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['pteam_id'], ['pteam.pteam_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['account.user_id'], ),
    sa.PrimaryKeyConstraint('pteam_id', 'user_id')
    )
    op.create_index(op.f('ix_pteamauthority_pteam_id'), 'pteamauthority', ['pteam_id'], unique=False)
    op.create_index(op.f('ix_pteamauthority_user_id'), 'pteamauthority', ['user_id'], unique=False)
    op.create_table('pteaminvitation',
    sa.Column('invitation_id', sa.String(length=36), nullable=False),
    sa.Column('pteam_id', sa.String(length=36), nullable=False),
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('expiration', sa.DateTime(), nullable=False),
    sa.Column('limit_count', sa.Integer(), nullable=True),
    sa.Column('used_count', sa.Integer(), server_default='0', nullable=False),
    sa.Column('authority', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['pteam_id'], ['pteam.pteam_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['account.user_id'], ),
    sa.PrimaryKeyConstraint('invitation_id')
    )
    op.create_index(op.f('ix_pteaminvitation_pteam_id'), 'pteaminvitation', ['pteam_id'], unique=False)
    op.create_index(op.f('ix_pteaminvitation_user_id'), 'pteaminvitation', ['user_id'], unique=False)
    op.create_table('pteamtag',
    sa.Column('pteam_id', sa.String(length=36), nullable=False),
    sa.Column('tag_id', sa.String(length=36), nullable=False),
    sa.Column('refs', sa.ARRAY(sa.JSON()), nullable=False),
    sa.Column('text', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['pteam_id'], ['pteam.pteam_id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['tag_id'], ['tag.tag_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('pteam_id', 'tag_id')
    )
    op.create_index(op.f('ix_pteamtag_pteam_id'), 'pteamtag', ['pteam_id'], unique=False)
    op.create_index(op.f('ix_pteamtag_tag_id'), 'pteamtag', ['tag_id'], unique=False)
    op.create_table('secbadge',
    sa.Column('badge_id', sa.String(length=36), nullable=False),
    sa.Column('badge_name', sa.String(length=255), nullable=False),
    sa.Column('image_url', sa.String(length=255), nullable=False),
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('created_by', sa.String(length=36), nullable=False),
    sa.Column('obtained_at', sa.DateTime(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('expired_at', sa.DateTime(), nullable=True),
    sa.Column('metadata_json', sa.JSON(), nullable=False),
    sa.Column('priority', sa.Integer(), nullable=False),
    sa.Column('difficulty', sa.Enum('low', 'middle', 'high', name='difficulty'), nullable=False),
    sa.Column('badge_type', sa.ARRAY(sa.Enum('skill', 'performance', 'position', name='badgetype')), nullable=False),
    sa.Column('certifier_type', sa.Enum('trusted_third_party', 'coworker', 'myself', 'system', name='certifiertype'), nullable=False),
    sa.Column('pteam_id', sa.String(length=36), nullable=False),
    sa.ForeignKeyConstraint(['created_by'], ['account.user_id'], ),
    sa.ForeignKeyConstraint(['pteam_id'], ['pteam.pteam_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['account.user_id'], ),
    sa.PrimaryKeyConstraint('badge_id')
    )
    op.create_index(op.f('ix_secbadge_created_by'), 'secbadge', ['created_by'], unique=False)
    op.create_index(op.f('ix_secbadge_pteam_id'), 'secbadge', ['pteam_id'], unique=False)
    op.create_index(op.f('ix_secbadge_user_id'), 'secbadge', ['user_id'], unique=False)
    op.create_foreign_key("account_favorite_badge_fkey", 'account', 'secbadge', ['favorite_badge'], ['badge_id'])
    op.create_table('topic',
    sa.Column('topic_id', sa.String(length=36), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('abstract', sa.Text(), nullable=False),
    sa.Column('threat_impact', sa.Integer(), nullable=False),
    sa.Column('created_by', sa.String(length=36), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('content_fingerprint', sa.Text(), nullable=False),
    sa.Column('disabled', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['created_by'], ['account.user_id'], ),
    sa.PrimaryKeyConstraint('topic_id')
    )
    op.create_index(op.f('ix_topic_created_by'), 'topic', ['created_by'], unique=False)
    op.create_table('zone',
    sa.Column('zone_name', sa.String(length=255), nullable=False),
    sa.Column('zone_info', sa.Text(), nullable=False),
    sa.Column('gteam_id', sa.String(length=36), nullable=False),
    sa.Column('created_by', sa.String(length=36), nullable=False),
    sa.Column('archived', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['created_by'], ['account.user_id'], ),
    sa.ForeignKeyConstraint(['gteam_id'], ['gteam.gteam_id'], ),
    sa.PrimaryKeyConstraint('zone_name')
    )
    op.create_index(op.f('ix_zone_created_by'), 'zone', ['created_by'], unique=False)
    op.create_index(op.f('ix_zone_gteam_id'), 'zone', ['gteam_id'], unique=False)
    op.create_table('ateamtopiccomment',
    sa.Column('comment_id', sa.String(length=36), nullable=False),
    sa.Column('topic_id', sa.String(length=36), nullable=False),
    sa.Column('ateam_id', sa.String(length=36), nullable=False),
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('comment', sa.Text(), nullable=False),
    sa.ForeignKeyConstraint(['ateam_id'], ['ateam.ateam_id'], ),
    sa.ForeignKeyConstraint(['topic_id'], ['topic.topic_id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['account.user_id'], ),
    sa.PrimaryKeyConstraint('comment_id')
    )
    op.create_index(op.f('ix_ateamtopiccomment_ateam_id'), 'ateamtopiccomment', ['ateam_id'], unique=False)
    op.create_index(op.f('ix_ateamtopiccomment_topic_id'), 'ateamtopiccomment', ['topic_id'], unique=False)
    op.create_index(op.f('ix_ateamtopiccomment_user_id'), 'ateamtopiccomment', ['user_id'], unique=False)
    op.create_table('pteamtopictagstatus',
    sa.Column('status_id', sa.String(length=36), nullable=False),
    sa.Column('pteam_id', sa.String(length=36), nullable=False),
    sa.Column('topic_id', sa.String(length=36), nullable=False),
    sa.Column('tag_id', sa.String(length=36), nullable=False),
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('topic_status', sa.Enum('alerted', 'acknowledged', 'scheduled', 'completed', name='topicstatustype'), nullable=False),
    sa.Column('note', sa.Text(), nullable=True),
    sa.Column('logging_ids', sa.ARRAY(sa.String(length=36)), nullable=False),
    sa.Column('assignees', sa.ARRAY(sa.String(length=36)), nullable=False),
    sa.Column('scheduled_at', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.ForeignKeyConstraint(['pteam_id'], ['pteam.pteam_id'], ),
    sa.ForeignKeyConstraint(['tag_id'], ['tag.tag_id'], ),
    sa.ForeignKeyConstraint(['topic_id'], ['topic.topic_id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['account.user_id'], ),
    sa.PrimaryKeyConstraint('status_id')
    )
    op.create_index(op.f('ix_pteamtopictagstatus_pteam_id'), 'pteamtopictagstatus', ['pteam_id'], unique=False)
    op.create_index(op.f('ix_pteamtopictagstatus_tag_id'), 'pteamtopictagstatus', ['tag_id'], unique=False)
    op.create_index(op.f('ix_pteamtopictagstatus_topic_id'), 'pteamtopictagstatus', ['topic_id'], unique=False)
    op.create_index(op.f('ix_pteamtopictagstatus_user_id'), 'pteamtopictagstatus', ['user_id'], unique=False)
    op.create_table('pteamzone',
    sa.Column('pteam_id', sa.String(length=36), nullable=False),
    sa.Column('zone_name', sa.String(length=255), nullable=False),
    sa.ForeignKeyConstraint(['pteam_id'], ['pteam.pteam_id'], ),
    sa.ForeignKeyConstraint(['zone_name'], ['zone.zone_name'], ),
    sa.PrimaryKeyConstraint('pteam_id', 'zone_name')
    )
    op.create_index(op.f('ix_pteamzone_pteam_id'), 'pteamzone', ['pteam_id'], unique=False)
    op.create_index(op.f('ix_pteamzone_zone_name'), 'pteamzone', ['zone_name'], unique=False)
    op.create_table('topicaction',
    sa.Column('action_id', sa.String(length=36), nullable=False),
    sa.Column('topic_id', sa.String(length=36), nullable=False),
    sa.Column('action', sa.Text(), nullable=False),
    sa.Column('action_type', sa.Enum('elimination', 'transfer', 'mitigation', 'acceptance', 'detection', 'rejection', name='actiontype'), nullable=False),
    sa.Column('recommended', sa.Boolean(), nullable=False),
    sa.Column('ext', sa.JSON(), nullable=False),
    sa.Column('created_by', sa.String(length=36), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.ForeignKeyConstraint(['created_by'], ['account.user_id'], ),
    sa.ForeignKeyConstraint(['topic_id'], ['topic.topic_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('action_id')
    )
    op.create_index(op.f('ix_topicaction_created_by'), 'topicaction', ['created_by'], unique=False)
    op.create_index(op.f('ix_topicaction_topic_id'), 'topicaction', ['topic_id'], unique=False)
    op.create_table('topicmisptag',
    sa.Column('topic_id', sa.String(length=36), nullable=False),
    sa.Column('tag_id', sa.String(length=36), nullable=False),
    sa.ForeignKeyConstraint(['tag_id'], ['misptag.tag_id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['topic_id'], ['topic.topic_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('topic_id', 'tag_id')
    )
    op.create_index(op.f('ix_topicmisptag_tag_id'), 'topicmisptag', ['tag_id'], unique=False)
    op.create_index(op.f('ix_topicmisptag_topic_id'), 'topicmisptag', ['topic_id'], unique=False)
    op.create_table('topictag',
    sa.Column('topic_id', sa.String(length=36), nullable=False),
    sa.Column('tag_id', sa.String(length=36), nullable=False),
    sa.ForeignKeyConstraint(['tag_id'], ['tag.tag_id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['topic_id'], ['topic.topic_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('topic_id', 'tag_id')
    )
    op.create_index(op.f('ix_topictag_tag_id'), 'topictag', ['tag_id'], unique=False)
    op.create_index(op.f('ix_topictag_topic_id'), 'topictag', ['topic_id'], unique=False)
    op.create_table('topiczone',
    sa.Column('topic_id', sa.String(length=36), nullable=False),
    sa.Column('zone_name', sa.String(length=255), nullable=False),
    sa.ForeignKeyConstraint(['topic_id'], ['topic.topic_id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['zone_name'], ['zone.zone_name'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('topic_id', 'zone_name')
    )
    op.create_index(op.f('ix_topiczone_topic_id'), 'topiczone', ['topic_id'], unique=False)
    op.create_index(op.f('ix_topiczone_zone_name'), 'topiczone', ['zone_name'], unique=False)
    op.create_table('actionzone',
    sa.Column('action_id', sa.String(length=36), nullable=False),
    sa.Column('zone_name', sa.String(length=255), nullable=False),
    sa.ForeignKeyConstraint(['action_id'], ['topicaction.action_id'], ),
    sa.ForeignKeyConstraint(['zone_name'], ['zone.zone_name'], ),
    sa.PrimaryKeyConstraint('action_id', 'zone_name')
    )
    op.create_index(op.f('ix_actionzone_action_id'), 'actionzone', ['action_id'], unique=False)
    op.create_index(op.f('ix_actionzone_zone_name'), 'actionzone', ['zone_name'], unique=False)
    op.create_table('currentpteamtopictagstatus',
    sa.Column('pteam_id', sa.String(length=36), nullable=False),
    sa.Column('topic_id', sa.String(length=36), nullable=False),
    sa.Column('tag_id', sa.String(length=36), nullable=False),
    sa.Column('status_id', sa.String(length=36), nullable=True),
    sa.Column('topic_status', sa.Enum('alerted', 'acknowledged', 'scheduled', 'completed', name='topicstatustype'), nullable=True),
    sa.Column('threat_impact', sa.Integer(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['pteam_id'], ['pteam.pteam_id'], ),
    sa.ForeignKeyConstraint(['status_id'], ['pteamtopictagstatus.status_id'], ),
    sa.ForeignKeyConstraint(['tag_id'], ['tag.tag_id'], ),
    sa.ForeignKeyConstraint(['topic_id'], ['topic.topic_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('pteam_id', 'topic_id', 'tag_id')
    )
    op.create_index(op.f('ix_currentpteamtopictagstatus_pteam_id'), 'currentpteamtopictagstatus', ['pteam_id'], unique=False)
    op.create_index(op.f('ix_currentpteamtopictagstatus_status_id'), 'currentpteamtopictagstatus', ['status_id'], unique=False)
    op.create_index(op.f('ix_currentpteamtopictagstatus_tag_id'), 'currentpteamtopictagstatus', ['tag_id'], unique=False)
    op.create_index(op.f('ix_currentpteamtopictagstatus_topic_id'), 'currentpteamtopictagstatus', ['topic_id'], unique=False)
    #
    insert_threatconnectome_system_accounts(account_table)
    # ### end Alembic commands ###


def downgrade() -> None:
    op.drop_index(op.f('ix_currentpteamtopictagstatus_topic_id'), table_name='currentpteamtopictagstatus')
    op.drop_index(op.f('ix_currentpteamtopictagstatus_tag_id'), table_name='currentpteamtopictagstatus')
    op.drop_index(op.f('ix_currentpteamtopictagstatus_status_id'), table_name='currentpteamtopictagstatus')
    op.drop_index(op.f('ix_currentpteamtopictagstatus_pteam_id'), table_name='currentpteamtopictagstatus')
    op.drop_table('currentpteamtopictagstatus')
    op.drop_index(op.f('ix_actionzone_zone_name'), table_name='actionzone')
    op.drop_index(op.f('ix_actionzone_action_id'), table_name='actionzone')
    op.drop_table('actionzone')
    op.drop_index(op.f('ix_topiczone_zone_name'), table_name='topiczone')
    op.drop_index(op.f('ix_topiczone_topic_id'), table_name='topiczone')
    op.drop_table('topiczone')
    op.drop_index(op.f('ix_topictag_topic_id'), table_name='topictag')
    op.drop_index(op.f('ix_topictag_tag_id'), table_name='topictag')
    op.drop_table('topictag')
    op.drop_index(op.f('ix_topicmisptag_topic_id'), table_name='topicmisptag')
    op.drop_index(op.f('ix_topicmisptag_tag_id'), table_name='topicmisptag')
    op.drop_table('topicmisptag')
    op.drop_index(op.f('ix_topicaction_topic_id'), table_name='topicaction')
    op.drop_index(op.f('ix_topicaction_created_by'), table_name='topicaction')
    op.drop_table('topicaction')
    op.drop_index(op.f('ix_pteamzone_zone_name'), table_name='pteamzone')
    op.drop_index(op.f('ix_pteamzone_pteam_id'), table_name='pteamzone')
    op.drop_table('pteamzone')
    op.drop_index(op.f('ix_pteamtopictagstatus_user_id'), table_name='pteamtopictagstatus')
    op.drop_index(op.f('ix_pteamtopictagstatus_topic_id'), table_name='pteamtopictagstatus')
    op.drop_index(op.f('ix_pteamtopictagstatus_tag_id'), table_name='pteamtopictagstatus')
    op.drop_index(op.f('ix_pteamtopictagstatus_pteam_id'), table_name='pteamtopictagstatus')
    op.drop_table('pteamtopictagstatus')
    op.drop_index(op.f('ix_ateamtopiccomment_user_id'), table_name='ateamtopiccomment')
    op.drop_index(op.f('ix_ateamtopiccomment_topic_id'), table_name='ateamtopiccomment')
    op.drop_index(op.f('ix_ateamtopiccomment_ateam_id'), table_name='ateamtopiccomment')
    op.drop_table('ateamtopiccomment')
    op.drop_index(op.f('ix_zone_gteam_id'), table_name='zone')
    op.drop_index(op.f('ix_zone_created_by'), table_name='zone')
    op.drop_table('zone')
    op.drop_index(op.f('ix_topic_created_by'), table_name='topic')
    op.drop_table('topic')
    op.drop_index(op.f('ix_secbadge_user_id'), table_name='secbadge')
    op.drop_index(op.f('ix_secbadge_pteam_id'), table_name='secbadge')
    op.drop_index(op.f('ix_secbadge_created_by'), table_name='secbadge')
    op.drop_constraint("account_favorite_badge_fkey", table_name="account")
    op.drop_table('secbadge')
    op.drop_index(op.f('ix_pteamtag_tag_id'), table_name='pteamtag')
    op.drop_index(op.f('ix_pteamtag_pteam_id'), table_name='pteamtag')
    op.drop_table('pteamtag')
    op.drop_index(op.f('ix_pteaminvitation_user_id'), table_name='pteaminvitation')
    op.drop_index(op.f('ix_pteaminvitation_pteam_id'), table_name='pteaminvitation')
    op.drop_table('pteaminvitation')
    op.drop_index(op.f('ix_pteamauthority_user_id'), table_name='pteamauthority')
    op.drop_index(op.f('ix_pteamauthority_pteam_id'), table_name='pteamauthority')
    op.drop_table('pteamauthority')
    op.drop_index(op.f('ix_pteamaccount_user_id'), table_name='pteamaccount')
    op.drop_index(op.f('ix_pteamaccount_pteam_id'), table_name='pteamaccount')
    op.drop_table('pteamaccount')
    op.drop_index(op.f('ix_gteaminvitation_user_id'), table_name='gteaminvitation')
    op.drop_index(op.f('ix_gteaminvitation_gteam_id'), table_name='gteaminvitation')
    op.drop_table('gteaminvitation')
    op.drop_index(op.f('ix_gteamauthority_user_id'), table_name='gteamauthority')
    op.drop_index(op.f('ix_gteamauthority_gteam_id'), table_name='gteamauthority')
    op.drop_table('gteamauthority')
    op.drop_index(op.f('ix_gteamaccount_user_id'), table_name='gteamaccount')
    op.drop_index(op.f('ix_gteamaccount_gteam_id'), table_name='gteamaccount')
    op.drop_table('gteamaccount')
    op.drop_index(op.f('ix_ateamwatchingrequest_user_id'), table_name='ateamwatchingrequest')
    op.drop_index(op.f('ix_ateamwatchingrequest_ateam_id'), table_name='ateamwatchingrequest')
    op.drop_table('ateamwatchingrequest')
    op.drop_index(op.f('ix_ateampteam_pteam_id'), table_name='ateampteam')
    op.drop_index(op.f('ix_ateampteam_ateam_id'), table_name='ateampteam')
    op.drop_table('ateampteam')
    op.drop_index(op.f('ix_ateaminvitation_user_id'), table_name='ateaminvitation')
    op.drop_index(op.f('ix_ateaminvitation_ateam_id'), table_name='ateaminvitation')
    op.drop_table('ateaminvitation')
    op.drop_index(op.f('ix_ateamauthority_user_id'), table_name='ateamauthority')
    op.drop_index(op.f('ix_ateamauthority_ateam_id'), table_name='ateamauthority')
    op.drop_table('ateamauthority')
    op.drop_index(op.f('ix_ateamaccount_user_id'), table_name='ateamaccount')
    op.drop_index(op.f('ix_ateamaccount_ateam_id'), table_name='ateamaccount')
    op.drop_table('ateamaccount')
    op.drop_index(op.f('ix_actionlog_user_id'), table_name='actionlog')
    op.drop_index(op.f('ix_actionlog_pteam_id'), table_name='actionlog')
    op.drop_table('actionlog')
    op.drop_index(op.f('ix_tag_parent_name'), table_name='tag')
    op.drop_index(op.f('ix_tag_parent_id'), table_name='tag')
    op.drop_table('tag')
    op.drop_table('pteam')
    op.drop_table('misptag')
    op.drop_table('gteam')
    op.drop_table('ateam')
    op.drop_index(op.f('ix_account_favorite_badge'), table_name='account')
    op.drop_table('account')
    # drop auto generated Enums
    #   see https://github.com/sqlalchemy/alembic/issues/886
    sa.Enum(name="actiontype").drop(op.get_bind())
    sa.Enum(name="badgetype").drop(op.get_bind())
    sa.Enum(name="certifiertype").drop(op.get_bind())
    sa.Enum(name="difficulty").drop(op.get_bind())
    sa.Enum(name="topicstatustype").drop(op.get_bind())
    # ### end Alembic commands ###
