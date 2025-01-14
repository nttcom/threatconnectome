"""obsolete CurrentTicketStatus

Revision ID: 3f1137b70d1a
Revises: c0ce4f1cf87a
Create Date: 2024-11-17 23:43:22.486338

"""
import sqlalchemy as sa
import uuid
from alembic import op
from datetime import datetime
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import column, table

# revision identifiers, used by Alembic.
revision = '3f1137b70d1a'
down_revision = 'c0ce4f1cf87a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    connection = op.get_bind()
    now = datetime.now()

    # delete not-current ticket statuses
    connection.exec_driver_sql(
        "DELETE FROM TicketStatus WHERE status_id NOT IN "
        "  (SELECT status_id FROM currentticketstatus)"
    )

    # gen default ticket status if missing
    stateless_ticket_ids = [
        row.ticket_id for row in connection.exec_driver_sql(
            "SELECT ticket_id FROM Ticket WHERE ticket_id NOT IN "
            "  (SELECT ticket_id FROM ticketstatus)"
        )
    ]
    op.alter_column("ticketstatus", "user_id", nullable=True)
    ticket_status_table = table(
        "ticketstatus",
        column("status_id", sa.String(length=36)),
        column("ticket_id", sa.String(length=36)),
        column("user_id", sa.String(length=36)),
        column("note", sa.Text()),
        column("logging_ids", sa.ARRAY(sa.String(length=36))),
        column("assignees", sa.ARRAY(sa.String(length=36))),
        column("scheduled_at", sa.DateTime()),
        column("created_at", sa.DateTime()),
        column("topic_status", type_=sa.Enum(name="topicstatustype")),
    )
    op.bulk_insert(
        ticket_status_table,
        [
            {
                "status_id": str(uuid.uuid4()),
                "ticket_id": ticket_id,
                "user_id": None,
                "topic_status": "alerted",
                "note": None,
                "logging_ids": [],
                "assignees": [],
                "scheduled_at": None,
                "created_at": now,
                "action_logs": [],
            }
            for ticket_id in stateless_ticket_ids
        ],
    )

    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_currentticketstatus_status_id', table_name='currentticketstatus')
    op.drop_index('ix_currentticketstatus_ticket_id', table_name='currentticketstatus')
    op.drop_table('currentticketstatus')
    # ### end Alembic commands ###


def downgrade() -> None:
    op.create_table('currentticketstatus',
    sa.Column('current_status_id', sa.VARCHAR(length=36), autoincrement=False, nullable=False),
    sa.Column('ticket_id', sa.VARCHAR(length=36), autoincrement=False, nullable=False),
    sa.Column('status_id', sa.VARCHAR(length=36), autoincrement=False, nullable=True),
    sa.Column('threat_impact', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['status_id'], ['ticketstatus.status_id'], name='currentticketstatus_status_id_fkey'),
    sa.ForeignKeyConstraint(['ticket_id'], ['ticket.ticket_id'], name='currentticketstatus_ticket_id_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('current_status_id', name='currentticketstatus_pkey')
    )
    op.create_index('ix_currentticketstatus_ticket_id', 'currentticketstatus', ['ticket_id'], unique=True)
    op.create_index('ix_currentticketstatus_status_id', 'currentticketstatus', ['status_id'], unique=False)
    op.add_column(
        "currentticketstatus",
        sa.Column("topic_status", type_=sa.Enum(name="topicstatustype"), nullable=True),
    )

    # omit recovering current ticket status.

    op.alter_column("ticketstatus", "user_id", nullable=False)
