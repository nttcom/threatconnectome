"""alert threshold by ssvc_priority

Revision ID: e4ba4affc44f
Revises: 1fc28876e6e9
Create Date: 2024-09-05 03:27:52.173413

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e4ba4affc44f'
down_revision = '1fc28876e6e9'
branch_labels = None
depends_on = None

thresholds_map = {1: "IMMEDIATE", 2: "OUT_OF_CYCLE", 3: "SCHEDULED", 4: "DEFER"}


def upgrade() -> None:
    connection = op.get_bind()
    op.add_column(
        "pteam",
        sa.Column(
            "alert_ssvc_priority",
            sa.Enum(name="ssvcdeployerpriorityenum"),
            server_default="IMMEDIATE",
            nullable=False,
        ),
    )
    for threat_impact, ssvc_priority in thresholds_map.items():
        connection.exec_driver_sql(
            f"UPDATE pteam SET alert_ssvc_priority = '{ssvc_priority}'"
            f" where alert_threat_impact = '{threat_impact}'"
        )
    op.drop_column("pteam", "alert_threat_impact")


def downgrade() -> None:
    connection = op.get_bind()
    op.add_column("pteam", sa.Column("alert_threat_impact", sa.Integer(), nullable=True))
    for threat_impact, ssvc_priority in thresholds_map.items():
        connection.exec_driver_sql(
            f"UPDATE pteam SET alert_threat_impact = '{threat_impact}'"
            f" where alert_ssvc_priority = '{ssvc_priority}'"
        )
    op.drop_column("pteam", "alert_ssvc_priority")
