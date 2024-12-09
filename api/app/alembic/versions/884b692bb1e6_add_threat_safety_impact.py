"""add_threat_safety_impact

Revision ID: 884b692bb1e6
Revises: 79208ca4528e
Create Date: 2024-12-02 10:41:21.301343

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "884b692bb1e6"
down_revision = "79208ca4528e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("service", "safety_impact")
    op.add_column(
        "service",
        sa.Column(
            "service_safety_impact",
            type_=sa.Enum(name="safetyimpactenum"),
            server_default="NEGLIGIBLE",
            nullable=False,
        ),
    )
    op.add_column(
        "threat",
        sa.Column(
            "threat_safety_impact",
            type_=sa.Enum(name="safetyimpactenum"),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("threat", "threat_safety_impact")
    op.drop_column("service", "service_safety_impact")
    op.add_column(
        "service",
        sa.Column(
            "safety_impact",
            type_=sa.Enum(name="safetyimpactenum"),
            server_default=sa.text("'NEGLIGIBLE'::safetyimpactenum"),
            autoincrement=False,
            nullable=False,
        ),
    )
