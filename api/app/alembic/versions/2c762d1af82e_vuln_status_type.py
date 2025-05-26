"""vuln-status-type

Revision ID: 2c762d1af82e
Revises: 62a9068190ec
Create Date: 2025-05-26 00:49:22.652455

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "2c762d1af82e"
down_revision = "62a9068190ec"
branch_labels = None
depends_on = None


def upgrade() -> None:
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
            server_default="alerted",
            nullable=False,
        ),
    )
    op.alter_column("ticketstatus", "vuln_status", server_default=None, nullable=False)
    op.drop_column("ticketstatus", "topic_status")
    topic_status_type = sa.Enum(
        "alerted", "acknowledged", "scheduled", "completed", name="topicstatustype"
    )
    topic_status_type.drop(op.get_bind())


def downgrade() -> None:
    connection = op.get_bind()
    topic_status_type = sa.Enum(
        "alerted", "acknowledged", "scheduled", "completed", name="topicstatustype"
    )
    topic_status_type.create(connection)
    op.add_column(
        "ticketstatus",
        sa.Column(
            "topic_status",
            topic_status_type,
            autoincrement=False,
            server_default="alerted",
            nullable=False,
        ),
    )
    op.alter_column("ticketstatus", "topic_status", server_default=None, nullable=False)
    op.drop_column("ticketstatus", "vuln_status")
    vuln_status_type = sa.Enum(
        "alerted", "acknowledged", "scheduled", "completed", name="vulnstatustype"
    )
    vuln_status_type.drop(op.get_bind())
