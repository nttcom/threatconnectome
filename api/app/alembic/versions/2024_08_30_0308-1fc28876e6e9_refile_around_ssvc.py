"""refile around ssvc

Revision ID: 1fc28876e6e9
Revises: 145f9cc8c891
Create Date: 2024-08-30 03:08:48.237731

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '1fc28876e6e9'
down_revision = '145f9cc8c891'
branch_labels = None
depends_on = None


def upgrade() -> None:
    connection = op.get_bind()
    op.drop_column("topic", "automatable")
    op.drop_column("topic", "exploitation")
    op.drop_column("topic", "safety_impact")
    op.drop_column("service", "exposure")
    op.drop_column("service", "service_mission_impact")
    op.drop_column("dependency", "dependency_mission_impact")
    sa.Enum(name="exploitationenum").drop(connection)
    sa.Enum(name="safetyimpactenum").drop(connection)
    sa.Enum(name="exposureenum").drop(connection)
    sa.Enum(name="missionimpactenum").drop(connection)

    automatable_enum = sa.Enum("YES", "NO", name="automatableenum")
    automatable_enum.create(connection)
    exploitation_enum = sa.Enum("ACTIVE", "PUBLIC_POC", "NONE", name="exploitationenum")
    exploitation_enum.create(connection)
    safety_impact_enum = sa.Enum(
        "CATASTROPHIC", "CRITICAL", "MARGINAL", "NEGLIGIBLE", name="safetyimpactenum"
    )
    safety_impact_enum.create(connection)
    system_exposure_enum = sa.Enum("OPEN", "CONTROLLED", "SMALL", name="systemexposureenum")
    system_exposure_enum.create(connection)
    mission_impact_enum = sa.Enum(
        "MISSION_FAILURE",
        "MEF_FAILURE",
        "MEF_SUPPORT_CRIPPLED",
        "DEGRADED",
        name="missionimpactenum",
    )
    mission_impact_enum.create(connection)

    op.add_column(
        "topic",
        sa.Column("automatable", automatable_enum, server_default="YES", nullable=False),
    )
    op.add_column(
        "topic",
        sa.Column("exploitation", exploitation_enum, server_default="ACTIVE", nullable=False),
    )
    op.add_column(
        "service",
        sa.Column("system_exposure", system_exposure_enum, server_default="OPEN", nullable=False),
    )
    op.add_column(
        "service",
        sa.Column(
            "service_mission_impact",
            mission_impact_enum,
            server_default="MISSION_FAILURE",
            nullable=False,
        ),
    )
    op.add_column(
        "service",
        sa.Column("safety_impact", safety_impact_enum, server_default="NEGLIGIBLE", nullable=False),
    )
    op.add_column(
        "dependency",
        sa.Column(
            "dependency_mission_impact",
            mission_impact_enum,
            server_default="MISSION_FAILURE",
            nullable=True,
        ),
    )


def downgrade() -> None:
    connection = op.get_bind()
    op.drop_column("dependency", "dependency_mission_impact")
    op.drop_column("service", "safety_impact")
    op.drop_column("service", "service_mission_impact")
    op.drop_column("service", "system_exposure")
    op.drop_column("topic", "exploitation")
    op.drop_column("topic", "automatable")
    sa.Enum(name="missionimpactenum").drop(connection)
    sa.Enum(name="systemexposureenum").drop(connection)
    sa.Enum(name="safetyimpactenum").drop(connection)
    sa.Enum(name="exploitationenum").drop(connection)
    sa.Enum(name="automatableenum").drop(connection)

    exploitation_enum = sa.Enum("ACTIVE", "POC", "NONE", name="exploitationenum")
    exploitation_enum.create(connection)
    safety_impact_enum = sa.Enum(
        "CATASTROPHIC", "HAZARDOUS", "MAJOR", "MINOR", "NONE", name="safetyimpactenum"
    )
    safety_impact_enum.create(connection)
    exposure_enum = sa.Enum("OPEN", "CONTROLLED", "SMALL", name="exposureenum")
    exposure_enum.create(connection)
    mission_impact_enum = sa.Enum(
        "MISSION_FAILURE",
        "MEF_FAILURE",
        "MEF_SUPPORT_CRIPPLED",
        "DEGRADED",
        "NONE",
        name="missionimpactenum",
    )
    mission_impact_enum.create(connection)

    op.add_column(
        "topic",
        sa.Column("automatable", sa.Boolean(), server_default=sa.text("TRUE"), nullable=False),
    )
    op.add_column(
        "topic",
        sa.Column("exploitation", exploitation_enum, server_default="ACTIVE", nullable=False),
    )
    op.add_column(
        "topic",
        sa.Column(
            "safety_impact", safety_impact_enum, server_default="CATASTROPHIC", nullable=False
        ),
    )
    op.add_column(
        "service",
        sa.Column("exposure", exposure_enum, server_default="OPEN", nullable=False),
    )
    op.add_column(
        "service",
        sa.Column(
            "service_mission_impact",
            mission_impact_enum,
            server_default="MISSION_FAILURE",
            nullable=False,
        ),
    )
    op.add_column(
        "dependency",
        sa.Column(
            "dependency_mission_impact",
            mission_impact_enum,
            server_default="MISSION_FAILURE",
            nullable=True,
        ),
    )
