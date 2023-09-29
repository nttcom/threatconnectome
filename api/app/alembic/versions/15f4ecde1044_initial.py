"""Initial

Revision ID: 15f4ecde1044
Revises: 
Create Date: 2023-09-28 03:00:52.859957

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
revision = '15f4ecde1044'
down_revision = None
branch_labels = None
depends_on = None


def insert_threatconnectome_system_accounts(account_table) -> None:
    op.bulk_insert(
        account_table,
        [
            # Note:
            #   All entries should have *same keys*, otherwise some column can be ignored.
            #   Entries below will make SQL: 'INSERT INTO account ("userId", uid, email, disabled)
            #   VALUES (...), (...), (...)' based on the first entry. If only the 3rd entry has
            #   a key "years", it will be ignored (because the first entry does not have "years").
            {
                "userId": str(MEMBER_UUID),
                "uid": "(pseudo account: pteam member)",
                "email": None,
                "disabled": True,
            },
            {
                "userId": str(NOT_MEMBER_UUID),
                "uid": "(pseudo account: not pteam member)",
                "email": None,
                "disabled": True,
            },
            {
                "userId": str(SYSTEM_UUID),
                "uid": "(pseudo account: system)",
                "email": SYSTEM_EMAIL,
                "disabled": True,
            },
        ],
    )


def upgrade() -> None:
    account_table = op.create_table('account',
    sa.Column('userId', sa.String(length=36), nullable=False),
    sa.Column('uid', sa.Text(), nullable=True),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('disabled', sa.Boolean(), nullable=False),
    sa.Column('years', sa.Integer(), nullable=True),
    sa.Column('favoriteBadge', sa.String(length=36), nullable=True),
    sa.ForeignKeyConstraint(['favoriteBadge'], ['secbadge.badgeId'], use_alter=True),
    sa.PrimaryKeyConstraint('userId'),
    sa.UniqueConstraint('uid')
    )
    op.create_index(op.f('ix_account_favoriteBadge'), 'account', ['favoriteBadge'], unique=False)
    op.create_table('ateam',
    sa.Column('ateamId', sa.String(length=36), nullable=False),
    sa.Column('ateamName', sa.String(length=255), nullable=False),
    sa.Column('contactInfo', sa.String(length=255), nullable=False),
    sa.Column('slackWebhookUrl', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('ateamId')
    )
    op.create_table('gteam',
    sa.Column('gteamId', sa.String(length=36), nullable=False),
    sa.Column('gteamName', sa.String(length=255), nullable=False),
    sa.Column('contactInfo', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('gteamId')
    )
    op.create_table('misptag',
    sa.Column('tagId', sa.String(length=36), nullable=False),
    sa.Column('tagName', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('tagId')
    )
    op.create_table('pteam',
    sa.Column('pteamId', sa.String(length=36), nullable=False),
    sa.Column('pteamName', sa.String(length=255), nullable=False),
    sa.Column('contactInfo', sa.String(length=255), nullable=False),
    sa.Column('slackWebhookUrl', sa.String(length=255), nullable=False),
    sa.Column('alertThreatImpact', sa.Integer(), nullable=True),
    sa.Column('disabled', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('pteamId')
    )
    op.create_table('tag',
    sa.Column('tagId', sa.String(length=36), nullable=False),
    sa.Column('tagName', sa.Text(), nullable=False),
    sa.Column('parentId', sa.String(length=36), nullable=True),
    sa.Column('parentName', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['parentId'], ['tag.tagId'], ),
    sa.ForeignKeyConstraint(['parentName'], ['tag.tagName'], ),
    sa.PrimaryKeyConstraint('tagId'),
    sa.UniqueConstraint('tagName')
    )
    op.create_index(op.f('ix_tag_parentId'), 'tag', ['parentId'], unique=False)
    op.create_index(op.f('ix_tag_parentName'), 'tag', ['parentName'], unique=False)
    op.create_table('actionlog',
    sa.Column('loggingId', sa.String(length=36), nullable=False),
    sa.Column('actionId', sa.String(length=36), nullable=False),
    sa.Column('topicId', sa.String(length=36), nullable=False),
    sa.Column('action', sa.Text(), nullable=False),
    sa.Column('actionType', sa.Enum('elimination', 'transfer', 'mitigation', 'acceptance', 'detection', 'rejection', name='actiontype'), nullable=False),
    sa.Column('recommended', sa.Boolean(), nullable=False),
    sa.Column('userId', sa.String(length=36), nullable=True),
    sa.Column('pteamId', sa.String(length=36), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('executedAt', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('createdAt', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.ForeignKeyConstraint(['pteamId'], ['pteam.pteamId'], ),
    sa.ForeignKeyConstraint(['userId'], ['account.userId'], ),
    sa.PrimaryKeyConstraint('loggingId')
    )
    op.create_index(op.f('ix_actionlog_pteamId'), 'actionlog', ['pteamId'], unique=False)
    op.create_index(op.f('ix_actionlog_userId'), 'actionlog', ['userId'], unique=False)
    op.create_table('ateamaccount',
    sa.Column('ateamId', sa.String(length=36), nullable=False),
    sa.Column('userId', sa.String(length=36), nullable=False),
    sa.ForeignKeyConstraint(['ateamId'], ['ateam.ateamId'], ),
    sa.ForeignKeyConstraint(['userId'], ['account.userId'], ),
    sa.PrimaryKeyConstraint('ateamId', 'userId')
    )
    op.create_index(op.f('ix_ateamaccount_ateamId'), 'ateamaccount', ['ateamId'], unique=False)
    op.create_index(op.f('ix_ateamaccount_userId'), 'ateamaccount', ['userId'], unique=False)
    op.create_table('ateamauthority',
    sa.Column('ateamId', sa.String(length=36), nullable=False),
    sa.Column('userId', sa.String(length=36), nullable=False),
    sa.Column('authority', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['ateamId'], ['ateam.ateamId'], ),
    sa.ForeignKeyConstraint(['userId'], ['account.userId'], ),
    sa.PrimaryKeyConstraint('ateamId', 'userId')
    )
    op.create_index(op.f('ix_ateamauthority_ateamId'), 'ateamauthority', ['ateamId'], unique=False)
    op.create_index(op.f('ix_ateamauthority_userId'), 'ateamauthority', ['userId'], unique=False)
    op.create_table('ateaminvitation',
    sa.Column('invitationId', sa.String(length=36), nullable=False),
    sa.Column('ateamId', sa.String(length=36), nullable=False),
    sa.Column('userId', sa.String(length=36), nullable=False),
    sa.Column('expiration', sa.DateTime(), nullable=False),
    sa.Column('limitCount', sa.Integer(), nullable=True),
    sa.Column('usedCount', sa.Integer(), server_default='0', nullable=False),
    sa.Column('authority', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['ateamId'], ['ateam.ateamId'], ),
    sa.ForeignKeyConstraint(['userId'], ['account.userId'], ),
    sa.PrimaryKeyConstraint('invitationId')
    )
    op.create_index(op.f('ix_ateaminvitation_ateamId'), 'ateaminvitation', ['ateamId'], unique=False)
    op.create_index(op.f('ix_ateaminvitation_userId'), 'ateaminvitation', ['userId'], unique=False)
    op.create_table('ateampteam',
    sa.Column('ateamId', sa.String(length=36), nullable=False),
    sa.Column('pteamId', sa.String(length=36), nullable=False),
    sa.ForeignKeyConstraint(['ateamId'], ['ateam.ateamId'], ),
    sa.ForeignKeyConstraint(['pteamId'], ['pteam.pteamId'], ),
    sa.PrimaryKeyConstraint('ateamId', 'pteamId')
    )
    op.create_index(op.f('ix_ateampteam_ateamId'), 'ateampteam', ['ateamId'], unique=False)
    op.create_index(op.f('ix_ateampteam_pteamId'), 'ateampteam', ['pteamId'], unique=False)
    op.create_table('ateamwatchingrequest',
    sa.Column('requestId', sa.String(length=36), nullable=False),
    sa.Column('ateamId', sa.String(length=36), nullable=False),
    sa.Column('userId', sa.String(length=36), nullable=False),
    sa.Column('expiration', sa.DateTime(), nullable=False),
    sa.Column('limitCount', sa.Integer(), nullable=True),
    sa.Column('usedCount', sa.Integer(), server_default='0', nullable=False),
    sa.ForeignKeyConstraint(['ateamId'], ['ateam.ateamId'], ),
    sa.ForeignKeyConstraint(['userId'], ['account.userId'], ),
    sa.PrimaryKeyConstraint('requestId')
    )
    op.create_index(op.f('ix_ateamwatchingrequest_ateamId'), 'ateamwatchingrequest', ['ateamId'], unique=False)
    op.create_index(op.f('ix_ateamwatchingrequest_userId'), 'ateamwatchingrequest', ['userId'], unique=False)
    op.create_table('gteamaccount',
    sa.Column('gteamId', sa.String(length=36), nullable=False),
    sa.Column('userId', sa.String(length=36), nullable=False),
    sa.ForeignKeyConstraint(['gteamId'], ['gteam.gteamId'], ),
    sa.ForeignKeyConstraint(['userId'], ['account.userId'], ),
    sa.PrimaryKeyConstraint('gteamId', 'userId')
    )
    op.create_index(op.f('ix_gteamaccount_gteamId'), 'gteamaccount', ['gteamId'], unique=False)
    op.create_index(op.f('ix_gteamaccount_userId'), 'gteamaccount', ['userId'], unique=False)
    op.create_table('gteamauthority',
    sa.Column('gteamId', sa.String(length=36), nullable=False),
    sa.Column('userId', sa.String(length=36), nullable=False),
    sa.Column('authority', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['gteamId'], ['gteam.gteamId'], ),
    sa.ForeignKeyConstraint(['userId'], ['account.userId'], ),
    sa.PrimaryKeyConstraint('gteamId', 'userId')
    )
    op.create_index(op.f('ix_gteamauthority_gteamId'), 'gteamauthority', ['gteamId'], unique=False)
    op.create_index(op.f('ix_gteamauthority_userId'), 'gteamauthority', ['userId'], unique=False)
    op.create_table('gteaminvitation',
    sa.Column('invitationId', sa.String(length=36), nullable=False),
    sa.Column('gteamId', sa.String(length=36), nullable=False),
    sa.Column('userId', sa.String(length=36), nullable=False),
    sa.Column('expiration', sa.DateTime(), nullable=False),
    sa.Column('limitCount', sa.Integer(), nullable=True),
    sa.Column('usedCount', sa.Integer(), server_default='0', nullable=False),
    sa.Column('authority', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['gteamId'], ['gteam.gteamId'], ),
    sa.ForeignKeyConstraint(['userId'], ['account.userId'], ),
    sa.PrimaryKeyConstraint('invitationId')
    )
    op.create_index(op.f('ix_gteaminvitation_gteamId'), 'gteaminvitation', ['gteamId'], unique=False)
    op.create_index(op.f('ix_gteaminvitation_userId'), 'gteaminvitation', ['userId'], unique=False)
    op.create_table('pteamaccount',
    sa.Column('pteamId', sa.String(length=36), nullable=False),
    sa.Column('userId', sa.String(length=36), nullable=False),
    sa.ForeignKeyConstraint(['pteamId'], ['pteam.pteamId'], ),
    sa.ForeignKeyConstraint(['userId'], ['account.userId'], ),
    sa.PrimaryKeyConstraint('pteamId', 'userId')
    )
    op.create_index(op.f('ix_pteamaccount_pteamId'), 'pteamaccount', ['pteamId'], unique=False)
    op.create_index(op.f('ix_pteamaccount_userId'), 'pteamaccount', ['userId'], unique=False)
    op.create_table('pteamauthority',
    sa.Column('pteamId', sa.String(length=36), nullable=False),
    sa.Column('userId', sa.String(length=36), nullable=False),
    sa.Column('authority', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['pteamId'], ['pteam.pteamId'], ),
    sa.ForeignKeyConstraint(['userId'], ['account.userId'], ),
    sa.PrimaryKeyConstraint('pteamId', 'userId')
    )
    op.create_index(op.f('ix_pteamauthority_pteamId'), 'pteamauthority', ['pteamId'], unique=False)
    op.create_index(op.f('ix_pteamauthority_userId'), 'pteamauthority', ['userId'], unique=False)
    op.create_table('pteaminvitation',
    sa.Column('invitationId', sa.String(length=36), nullable=False),
    sa.Column('pteamId', sa.String(length=36), nullable=False),
    sa.Column('userId', sa.String(length=36), nullable=False),
    sa.Column('expiration', sa.DateTime(), nullable=False),
    sa.Column('limitCount', sa.Integer(), nullable=True),
    sa.Column('usedCount', sa.Integer(), server_default='0', nullable=False),
    sa.Column('authority', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['pteamId'], ['pteam.pteamId'], ),
    sa.ForeignKeyConstraint(['userId'], ['account.userId'], ),
    sa.PrimaryKeyConstraint('invitationId')
    )
    op.create_index(op.f('ix_pteaminvitation_pteamId'), 'pteaminvitation', ['pteamId'], unique=False)
    op.create_index(op.f('ix_pteaminvitation_userId'), 'pteaminvitation', ['userId'], unique=False)
    op.create_table('pteamtag',
    sa.Column('pteamId', sa.String(length=36), nullable=False),
    sa.Column('tagId', sa.String(length=36), nullable=False),
    sa.Column('refs', sa.ARRAY(sa.JSON()), nullable=False),
    sa.Column('text', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['pteamId'], ['pteam.pteamId'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['tagId'], ['tag.tagId'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('pteamId', 'tagId')
    )
    op.create_index(op.f('ix_pteamtag_pteamId'), 'pteamtag', ['pteamId'], unique=False)
    op.create_index(op.f('ix_pteamtag_tagId'), 'pteamtag', ['tagId'], unique=False)
    op.create_table('secbadge',
    sa.Column('badgeId', sa.String(length=36), nullable=False),
    sa.Column('badgeName', sa.String(length=255), nullable=False),
    sa.Column('imageUrl', sa.String(length=255), nullable=False),
    sa.Column('userId', sa.String(length=36), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('createdBy', sa.String(length=36), nullable=False),
    sa.Column('obtainedAt', sa.DateTime(), nullable=False),
    sa.Column('createdAt', sa.DateTime(), nullable=False),
    sa.Column('expiredAt', sa.DateTime(), nullable=True),
    sa.Column('metadataJson', sa.JSON(), nullable=False),
    sa.Column('priority', sa.Integer(), nullable=False),
    sa.Column('difficulty', sa.Enum('low', 'middle', 'high', name='difficulty'), nullable=False),
    sa.Column('badgeType', sa.ARRAY(sa.Enum('skill', 'performance', 'position', name='badgetype')), nullable=False),
    sa.Column('certifierType', sa.Enum('trusted_third_party', 'coworker', 'myself', 'system', name='certifiertype'), nullable=False),
    sa.Column('pteamId', sa.String(length=36), nullable=False),
    sa.ForeignKeyConstraint(['createdBy'], ['account.userId'], ),
    sa.ForeignKeyConstraint(['pteamId'], ['pteam.pteamId'], ),
    sa.ForeignKeyConstraint(['userId'], ['account.userId'], ),
    sa.PrimaryKeyConstraint('badgeId')
    )
    op.create_index(op.f('ix_secbadge_createdBy'), 'secbadge', ['createdBy'], unique=False)
    op.create_index(op.f('ix_secbadge_pteamId'), 'secbadge', ['pteamId'], unique=False)
    op.create_index(op.f('ix_secbadge_userId'), 'secbadge', ['userId'], unique=False)
    op.create_table('topic',
    sa.Column('topicId', sa.String(length=36), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('abstract', sa.Text(), nullable=False),
    sa.Column('threatImpact', sa.Integer(), nullable=False),
    sa.Column('createdBy', sa.String(length=36), nullable=False),
    sa.Column('createdAt', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updatedAt', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('content_fingerprint', sa.Text(), nullable=False),
    sa.Column('disabled', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['createdBy'], ['account.userId'], ),
    sa.PrimaryKeyConstraint('topicId')
    )
    op.create_index(op.f('ix_topic_createdBy'), 'topic', ['createdBy'], unique=False)
    op.create_table('zone',
    sa.Column('zoneName', sa.String(length=255), nullable=False),
    sa.Column('zoneInfo', sa.Text(), nullable=False),
    sa.Column('gteamId', sa.String(length=36), nullable=False),
    sa.Column('createdBy', sa.String(length=36), nullable=False),
    sa.Column('archived', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['createdBy'], ['account.userId'], ),
    sa.ForeignKeyConstraint(['gteamId'], ['gteam.gteamId'], ),
    sa.PrimaryKeyConstraint('zoneName')
    )
    op.create_index(op.f('ix_zone_createdBy'), 'zone', ['createdBy'], unique=False)
    op.create_index(op.f('ix_zone_gteamId'), 'zone', ['gteamId'], unique=False)
    op.create_table('ateamtopiccomment',
    sa.Column('commentId', sa.String(length=36), nullable=False),
    sa.Column('topicId', sa.String(length=36), nullable=False),
    sa.Column('ateamId', sa.String(length=36), nullable=False),
    sa.Column('userId', sa.String(length=36), nullable=False),
    sa.Column('createdAt', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updatedAt', sa.DateTime(), nullable=True),
    sa.Column('comment', sa.Text(), nullable=False),
    sa.ForeignKeyConstraint(['ateamId'], ['ateam.ateamId'], ),
    sa.ForeignKeyConstraint(['topicId'], ['topic.topicId'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['userId'], ['account.userId'], ),
    sa.PrimaryKeyConstraint('commentId')
    )
    op.create_index(op.f('ix_ateamtopiccomment_ateamId'), 'ateamtopiccomment', ['ateamId'], unique=False)
    op.create_index(op.f('ix_ateamtopiccomment_topicId'), 'ateamtopiccomment', ['topicId'], unique=False)
    op.create_index(op.f('ix_ateamtopiccomment_userId'), 'ateamtopiccomment', ['userId'], unique=False)
    op.create_table('pteamtopictagstatus',
    sa.Column('statusId', sa.String(length=36), nullable=False),
    sa.Column('pteamId', sa.String(length=36), nullable=False),
    sa.Column('topicId', sa.String(length=36), nullable=False),
    sa.Column('tagId', sa.String(length=36), nullable=False),
    sa.Column('userId', sa.String(length=36), nullable=False),
    sa.Column('topicStatus', sa.Enum('alerted', 'acknowledged', 'scheduled', 'completed', name='topicstatustype'), nullable=False),
    sa.Column('note', sa.Text(), nullable=True),
    sa.Column('loggingIds', sa.ARRAY(sa.String(length=36)), nullable=False),
    sa.Column('assignees', sa.ARRAY(sa.String(length=36)), nullable=False),
    sa.Column('scheduledAt', sa.DateTime(), nullable=True),
    sa.Column('createdAt', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.ForeignKeyConstraint(['pteamId'], ['pteam.pteamId'], ),
    sa.ForeignKeyConstraint(['tagId'], ['tag.tagId'], ),
    sa.ForeignKeyConstraint(['topicId'], ['topic.topicId'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['userId'], ['account.userId'], ),
    sa.PrimaryKeyConstraint('statusId')
    )
    op.create_index(op.f('ix_pteamtopictagstatus_pteamId'), 'pteamtopictagstatus', ['pteamId'], unique=False)
    op.create_index(op.f('ix_pteamtopictagstatus_tagId'), 'pteamtopictagstatus', ['tagId'], unique=False)
    op.create_index(op.f('ix_pteamtopictagstatus_topicId'), 'pteamtopictagstatus', ['topicId'], unique=False)
    op.create_index(op.f('ix_pteamtopictagstatus_userId'), 'pteamtopictagstatus', ['userId'], unique=False)
    op.create_table('pteamzone',
    sa.Column('pteamId', sa.String(length=36), nullable=False),
    sa.Column('zoneName', sa.String(length=255), nullable=False),
    sa.ForeignKeyConstraint(['pteamId'], ['pteam.pteamId'], ),
    sa.ForeignKeyConstraint(['zoneName'], ['zone.zoneName'], ),
    sa.PrimaryKeyConstraint('pteamId', 'zoneName')
    )
    op.create_index(op.f('ix_pteamzone_pteamId'), 'pteamzone', ['pteamId'], unique=False)
    op.create_index(op.f('ix_pteamzone_zoneName'), 'pteamzone', ['zoneName'], unique=False)
    op.create_table('topicaction',
    sa.Column('actionId', sa.String(length=36), nullable=False),
    sa.Column('topicId', sa.String(length=36), nullable=False),
    sa.Column('action', sa.Text(), nullable=False),
    sa.Column('actionType', sa.Enum('elimination', 'transfer', 'mitigation', 'acceptance', 'detection', 'rejection', name='actiontype'), nullable=False),
    sa.Column('recommended', sa.Boolean(), nullable=False),
    sa.Column('ext', sa.JSON(), nullable=False),
    sa.Column('createdBy', sa.String(length=36), nullable=False),
    sa.Column('createdAt', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.ForeignKeyConstraint(['createdBy'], ['account.userId'], ),
    sa.ForeignKeyConstraint(['topicId'], ['topic.topicId'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('actionId')
    )
    op.create_index(op.f('ix_topicaction_createdBy'), 'topicaction', ['createdBy'], unique=False)
    op.create_index(op.f('ix_topicaction_topicId'), 'topicaction', ['topicId'], unique=False)
    op.create_table('topicmisptag',
    sa.Column('topicId', sa.String(length=36), nullable=False),
    sa.Column('tagId', sa.String(length=36), nullable=False),
    sa.ForeignKeyConstraint(['tagId'], ['misptag.tagId'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['topicId'], ['topic.topicId'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('topicId', 'tagId')
    )
    op.create_index(op.f('ix_topicmisptag_tagId'), 'topicmisptag', ['tagId'], unique=False)
    op.create_index(op.f('ix_topicmisptag_topicId'), 'topicmisptag', ['topicId'], unique=False)
    op.create_table('topictag',
    sa.Column('topicId', sa.String(length=36), nullable=False),
    sa.Column('tagId', sa.String(length=36), nullable=False),
    sa.ForeignKeyConstraint(['tagId'], ['tag.tagId'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['topicId'], ['topic.topicId'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('topicId', 'tagId')
    )
    op.create_index(op.f('ix_topictag_tagId'), 'topictag', ['tagId'], unique=False)
    op.create_index(op.f('ix_topictag_topicId'), 'topictag', ['topicId'], unique=False)
    op.create_table('topiczone',
    sa.Column('topicId', sa.String(length=36), nullable=False),
    sa.Column('zoneName', sa.String(length=255), nullable=False),
    sa.ForeignKeyConstraint(['topicId'], ['topic.topicId'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['zoneName'], ['zone.zoneName'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('topicId', 'zoneName')
    )
    op.create_index(op.f('ix_topiczone_topicId'), 'topiczone', ['topicId'], unique=False)
    op.create_index(op.f('ix_topiczone_zoneName'), 'topiczone', ['zoneName'], unique=False)
    op.create_table('actionzone',
    sa.Column('actionId', sa.String(length=36), nullable=False),
    sa.Column('zoneName', sa.String(length=255), nullable=False),
    sa.ForeignKeyConstraint(['actionId'], ['topicaction.actionId'], ),
    sa.ForeignKeyConstraint(['zoneName'], ['zone.zoneName'], ),
    sa.PrimaryKeyConstraint('actionId', 'zoneName')
    )
    op.create_index(op.f('ix_actionzone_actionId'), 'actionzone', ['actionId'], unique=False)
    op.create_index(op.f('ix_actionzone_zoneName'), 'actionzone', ['zoneName'], unique=False)
    op.create_table('currentpteamtopictagstatus',
    sa.Column('pteamId', sa.String(length=36), nullable=False),
    sa.Column('topicId', sa.String(length=36), nullable=False),
    sa.Column('tagId', sa.String(length=36), nullable=False),
    sa.Column('statusId', sa.String(length=36), nullable=True),
    sa.Column('topicStatus', sa.Enum('alerted', 'acknowledged', 'scheduled', 'completed', name='topicstatustype'), nullable=True),
    sa.Column('threatImpact', sa.Integer(), nullable=True),
    sa.Column('updatedAt', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['pteamId'], ['pteam.pteamId'], ),
    sa.ForeignKeyConstraint(['statusId'], ['pteamtopictagstatus.statusId'], ),
    sa.ForeignKeyConstraint(['tagId'], ['tag.tagId'], ),
    sa.ForeignKeyConstraint(['topicId'], ['topic.topicId'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('pteamId', 'topicId', 'tagId')
    )
    op.create_index(op.f('ix_currentpteamtopictagstatus_pteamId'), 'currentpteamtopictagstatus', ['pteamId'], unique=False)
    op.create_index(op.f('ix_currentpteamtopictagstatus_statusId'), 'currentpteamtopictagstatus', ['statusId'], unique=False)
    op.create_index(op.f('ix_currentpteamtopictagstatus_tagId'), 'currentpteamtopictagstatus', ['tagId'], unique=False)
    op.create_index(op.f('ix_currentpteamtopictagstatus_topicId'), 'currentpteamtopictagstatus', ['topicId'], unique=False)
    #
    insert_threatconnectome_system_accounts(account_table)
    # ### end Alembic commands ###


def downgrade() -> None:
    #
    op.drop_index(op.f('ix_currentpteamtopictagstatus_topicId'), table_name='currentpteamtopictagstatus')
    op.drop_index(op.f('ix_currentpteamtopictagstatus_tagId'), table_name='currentpteamtopictagstatus')
    op.drop_index(op.f('ix_currentpteamtopictagstatus_statusId'), table_name='currentpteamtopictagstatus')
    op.drop_index(op.f('ix_currentpteamtopictagstatus_pteamId'), table_name='currentpteamtopictagstatus')
    op.drop_table('currentpteamtopictagstatus')
    op.drop_index(op.f('ix_actionzone_zoneName'), table_name='actionzone')
    op.drop_index(op.f('ix_actionzone_actionId'), table_name='actionzone')
    op.drop_table('actionzone')
    op.drop_index(op.f('ix_topiczone_zoneName'), table_name='topiczone')
    op.drop_index(op.f('ix_topiczone_topicId'), table_name='topiczone')
    op.drop_table('topiczone')
    op.drop_index(op.f('ix_topictag_topicId'), table_name='topictag')
    op.drop_index(op.f('ix_topictag_tagId'), table_name='topictag')
    op.drop_table('topictag')
    op.drop_index(op.f('ix_topicmisptag_topicId'), table_name='topicmisptag')
    op.drop_index(op.f('ix_topicmisptag_tagId'), table_name='topicmisptag')
    op.drop_table('topicmisptag')
    op.drop_index(op.f('ix_topicaction_topicId'), table_name='topicaction')
    op.drop_index(op.f('ix_topicaction_createdBy'), table_name='topicaction')
    op.drop_table('topicaction')
    op.drop_index(op.f('ix_pteamzone_zoneName'), table_name='pteamzone')
    op.drop_index(op.f('ix_pteamzone_pteamId'), table_name='pteamzone')
    op.drop_table('pteamzone')
    op.drop_index(op.f('ix_pteamtopictagstatus_userId'), table_name='pteamtopictagstatus')
    op.drop_index(op.f('ix_pteamtopictagstatus_topicId'), table_name='pteamtopictagstatus')
    op.drop_index(op.f('ix_pteamtopictagstatus_tagId'), table_name='pteamtopictagstatus')
    op.drop_index(op.f('ix_pteamtopictagstatus_pteamId'), table_name='pteamtopictagstatus')
    op.drop_table('pteamtopictagstatus')
    op.drop_index(op.f('ix_ateamtopiccomment_userId'), table_name='ateamtopiccomment')
    op.drop_index(op.f('ix_ateamtopiccomment_topicId'), table_name='ateamtopiccomment')
    op.drop_index(op.f('ix_ateamtopiccomment_ateamId'), table_name='ateamtopiccomment')
    op.drop_table('ateamtopiccomment')
    op.drop_index(op.f('ix_zone_gteamId'), table_name='zone')
    op.drop_index(op.f('ix_zone_createdBy'), table_name='zone')
    op.drop_table('zone')
    op.drop_index(op.f('ix_topic_createdBy'), table_name='topic')
    op.drop_table('topic')
    op.drop_index(op.f('ix_secbadge_userId'), table_name='secbadge')
    op.drop_index(op.f('ix_secbadge_pteamId'), table_name='secbadge')
    op.drop_index(op.f('ix_secbadge_createdBy'), table_name='secbadge')
    op.drop_table('secbadge')
    op.drop_index(op.f('ix_pteamtag_tagId'), table_name='pteamtag')
    op.drop_index(op.f('ix_pteamtag_pteamId'), table_name='pteamtag')
    op.drop_table('pteamtag')
    op.drop_index(op.f('ix_pteaminvitation_userId'), table_name='pteaminvitation')
    op.drop_index(op.f('ix_pteaminvitation_pteamId'), table_name='pteaminvitation')
    op.drop_table('pteaminvitation')
    op.drop_index(op.f('ix_pteamauthority_userId'), table_name='pteamauthority')
    op.drop_index(op.f('ix_pteamauthority_pteamId'), table_name='pteamauthority')
    op.drop_table('pteamauthority')
    op.drop_index(op.f('ix_pteamaccount_userId'), table_name='pteamaccount')
    op.drop_index(op.f('ix_pteamaccount_pteamId'), table_name='pteamaccount')
    op.drop_table('pteamaccount')
    op.drop_index(op.f('ix_gteaminvitation_userId'), table_name='gteaminvitation')
    op.drop_index(op.f('ix_gteaminvitation_gteamId'), table_name='gteaminvitation')
    op.drop_table('gteaminvitation')
    op.drop_index(op.f('ix_gteamauthority_userId'), table_name='gteamauthority')
    op.drop_index(op.f('ix_gteamauthority_gteamId'), table_name='gteamauthority')
    op.drop_table('gteamauthority')
    op.drop_index(op.f('ix_gteamaccount_userId'), table_name='gteamaccount')
    op.drop_index(op.f('ix_gteamaccount_gteamId'), table_name='gteamaccount')
    op.drop_table('gteamaccount')
    op.drop_index(op.f('ix_ateamwatchingrequest_userId'), table_name='ateamwatchingrequest')
    op.drop_index(op.f('ix_ateamwatchingrequest_ateamId'), table_name='ateamwatchingrequest')
    op.drop_table('ateamwatchingrequest')
    op.drop_index(op.f('ix_ateampteam_pteamId'), table_name='ateampteam')
    op.drop_index(op.f('ix_ateampteam_ateamId'), table_name='ateampteam')
    op.drop_table('ateampteam')
    op.drop_index(op.f('ix_ateaminvitation_userId'), table_name='ateaminvitation')
    op.drop_index(op.f('ix_ateaminvitation_ateamId'), table_name='ateaminvitation')
    op.drop_table('ateaminvitation')
    op.drop_index(op.f('ix_ateamauthority_userId'), table_name='ateamauthority')
    op.drop_index(op.f('ix_ateamauthority_ateamId'), table_name='ateamauthority')
    op.drop_table('ateamauthority')
    op.drop_index(op.f('ix_ateamaccount_userId'), table_name='ateamaccount')
    op.drop_index(op.f('ix_ateamaccount_ateamId'), table_name='ateamaccount')
    op.drop_table('ateamaccount')
    op.drop_index(op.f('ix_actionlog_userId'), table_name='actionlog')
    op.drop_index(op.f('ix_actionlog_pteamId'), table_name='actionlog')
    op.drop_table('actionlog')
    op.drop_index(op.f('ix_tag_parentName'), table_name='tag')
    op.drop_index(op.f('ix_tag_parentId'), table_name='tag')
    op.drop_table('tag')
    op.drop_table('pteam')
    op.drop_table('misptag')
    op.drop_table('gteam')
    op.drop_table('ateam')
    op.drop_index(op.f('ix_account_favoriteBadge'), table_name='account')
    op.drop_table('account')
    # drop auto generated Enums
    #   see https://github.com/sqlalchemy/alembic/issues/886
    sa.Enum(name="actiontype").drop(op.get_bind())
    sa.Enum(name="badgetype").drop(op.get_bind())
    sa.Enum(name="certifiertype").drop(op.get_bind())
    sa.Enum(name="difficulty").drop(op.get_bind())
    sa.Enum(name="topicstatustype").drop(op.get_bind())
    # ### end Alembic commands ###
