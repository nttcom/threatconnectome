"""ticket_handling_status

Revision ID: 9dac8976dadb
Revises: 393003f456f5
Create Date: 2025-08-25 05:10:33.968787

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "9dac8976dadb"
down_revision = "393003f456f5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    connection = op.get_bind()
    ticket_handling_status_type = sa.Enum(
        "alerted", "acknowledged", "scheduled", "completed", name="tickethandlingstatustype"
    )
    ticket_handling_status_type.create(connection)
    op.add_column(
        "ticketstatus",
        sa.Column(
            "ticket_handling_status",
            ticket_handling_status_type,
            nullable=True,
        ),
    )
    connection.execute(
        sa.text(
            """
            UPDATE ticketstatus
            SET ticket_handling_status = vuln_status::text::tickethandlingstatustype
            """
        )
    )
    op.alter_column("ticketstatus", "ticket_handling_status", nullable=False)

    op.drop_column("ticketstatus", "vuln_status")
    vuln_status_type = sa.Enum(
        "alerted", "acknowledged", "scheduled", "completed", name="vulnstatustype"
    )
    vuln_status_type.drop(op.get_bind())


def downgrade() -> None:
    connection = op.get_bind()
    vuln_status_type = sa.Enum(
        "alerted", "acknowledged", "scheduled", "completed", name="vulnstatustype"
    )
    vuln_status_type.create(connection)
    op.add_column(
        "ticketstatus",
        sa.Column(
            "vuln_status",
            vuln_status_type,
            autoincrement=False,
            nullable=True,
        ),
    )
    connection.execute(
        sa.text(
            """
            UPDATE ticketstatus
            SET vuln_status = ticket_handling_status::text::vulnstatustype
            """
        )
    )
    op.alter_column("ticketstatus", "vuln_status", nullable=False)
    op.drop_column("ticketstatus", "ticket_handling_status")
    ticket_handling_status = sa.Enum(
        "alerted", "acknowledged", "scheduled", "completed", name="tickethandlingstatustype"
    )
    ticket_handling_status.drop(op.get_bind())
