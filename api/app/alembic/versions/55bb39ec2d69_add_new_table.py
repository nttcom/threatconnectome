"""add_new_table

Revision ID: 55bb39ec2d69
Revises: b51315587b5d
Create Date: 2024-06-28

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "55bb39ec2d69"
down_revision = "b51315587b5d"
branch_labels = None
depends_on = None


def _delete_actionlog() -> None:
    op.get_bind().exec_driver_sql("DELETE FROM actionlog")


def _delete_topic_disabled() -> None:
    op.get_bind().exec_driver_sql("DELETE FROM topic WHERE topic.disabled = TRUE")


def _delete_pteam_disabled() -> None:
    op.get_bind().exec_driver_sql("DELETE FROM pteam WHERE pteam.disabled = TRUE")


def upgrade() -> None:
    ## create Enum
    connection = op.get_bind()
    mission_impact_enum = sa.Enum(
        "MISSION_FAILURE", "MEF_FAILURE", "CRIPPLED", "DEGRADED", "NONE", name="missionimpactenum"
    )
    mission_impact_enum.create(connection)
    exposure_enum = sa.Enum("OPEN", "CONTROLLED", "SMALL", name="exposureenum")
    exposure_enum.create(connection)
    safety_impact_enum = sa.Enum(
        "CATASTROPHIC", "HAZARDOUS", "MAJOR", "MINOR", "NONE", name="safetyimpactenum"
    )
    safety_impact_enum.create(connection)
    exploitation_enum = sa.Enum("ACTIVE", "POC", "NONE", name="exploitationenum")
    exploitation_enum.create(connection)

    ## topic table
    op.add_column(
        "topic",
        sa.Column(
            "safety_impact", safety_impact_enum, server_default="CATASTROPHIC", nullable=False
        ),
    )
    op.add_column(
        "topic",
        sa.Column("exploitation", exploitation_enum, server_default="ACTIVE", nullable=False),
    )
    op.add_column(
        "topic",
        sa.Column("automatable", sa.Boolean(), server_default=sa.text("TRUE"), nullable=False),
    )

    ## service table
    op.add_column(
        "service", sa.Column("exposure", exposure_enum, server_default="OPEN", nullable=False)
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

    ## dependency table
    op.add_column(
        "dependency",
        sa.Column(
            "dependency_mission_impact", mission_impact_enum, server_default=None, nullable=True
        ),
    )
    op.add_column(
        "dependency",
        sa.Column("dependency_id", sa.VARCHAR(length=36), autoincrement=False),
    )
    op.execute(
        """
       UPDATE dependency
       SET dependency_id = gen_random_uuid()
       """
    )
    op.drop_constraint("dependency_pkey", table_name="dependency")
    op.create_primary_key("dependency_pkey", "dependency", ["dependency_id"])
    op.create_unique_constraint(
        "dependency_service_id_tag_id_version_target_key",
        "dependency",
        ["service_id", "tag_id", "version", "target"],
    )

    ## create threat table
    op.create_table(
        "threat",
        sa.Column("threat_id", sa.String(length=36), nullable=False),
        sa.Column("dependency_id", sa.String(length=36), nullable=False),
        sa.Column("topic_id", sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(
            ["dependency_id"], ["dependency.dependency_id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["topic_id"], ["topic.topic_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("threat_id"),
        sa.UniqueConstraint("dependency_id", "topic_id", name="threat_dependency_id_topic_id_key"),
    )
    op.create_index(op.f("ix_threat_topic_id"), "threat", ["topic_id"], unique=False)
    op.create_index(op.f("ix_threat_dependency_id"), "threat", ["dependency_id"], unique=False)

    ## create ticket table
    op.create_table(
        "ticket",
        sa.Column("ticket_id", sa.String(length=36), nullable=False),
        sa.Column("threat_id", sa.String(length=36), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False
        ),
        sa.Column(
            "ssvc_deployer_priority",
            sa.Enum(
                "IMMEDIATE", "OUT_OF_CYCLE", "SCHEDULED", "DEFER", name="ssvcdeployerpriorityenum"
            ),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["threat_id"], ["threat.threat_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("ticket_id"),
    )
    op.create_index(op.f("ix_ticket_threat_id"), "ticket", ["threat_id"], unique=True)

    ## create ticketstatus table
    op.create_table(
        "ticketstatus",
        sa.Column("status_id", sa.String(length=36), nullable=False),
        sa.Column("ticket_id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("logging_ids", sa.ARRAY(sa.String(length=36)), nullable=False),
        sa.Column("assignees", sa.ARRAY(sa.String(length=36)), nullable=False),
        sa.Column("scheduled_at", sa.DateTime(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False
        ),
        sa.ForeignKeyConstraint(["ticket_id"], ["ticket.ticket_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["account.user_id"]),
        sa.PrimaryKeyConstraint("status_id"),
    )
    op.create_index(op.f("ix_ticketstatus_ticket_id"), "ticketstatus", ["ticket_id"], unique=False)
    op.create_index(op.f("ix_ticketstatus_user_id"), "ticketstatus", ["user_id"], unique=False)
    op.add_column(
        "ticketstatus",
        sa.Column("topic_status", type_=sa.Enum(name="topicstatustype"), nullable=False),
    )

    ## create currentticketstatus table
    op.create_table(
        "currentticketstatus",
        sa.Column("current_status_id", sa.String(length=36), nullable=False),
        sa.Column("ticket_id", sa.String(length=36), nullable=False),
        sa.Column("status_id", sa.String(length=36), nullable=True),
        sa.Column("threat_impact", sa.Integer(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["status_id"],
            ["ticketstatus.status_id"],
        ),
        sa.ForeignKeyConstraint(["ticket_id"], ["ticket.ticket_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("current_status_id"),
    )
    op.create_index(
        op.f("ix_currentticketstatus_status_id"), "currentticketstatus", ["status_id"], unique=False
    )
    op.create_index(
        op.f("ix_currentticketstatus_ticket_id"), "currentticketstatus", ["ticket_id"], unique=True
    )
    op.add_column(
        "currentticketstatus",
        sa.Column("topic_status", type_=sa.Enum(name="topicstatustype"), nullable=True),
    )

    ## create alert table
    op.create_table(
        "alert",
        sa.Column("alert_id", sa.String(length=36), nullable=False),
        sa.Column("ticket_id", sa.String(length=36), nullable=True),
        sa.Column(
            "alerted_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False
        ),
        sa.Column("alert_content", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["ticket_id"], ["ticket.ticket_id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("alert_id"),
    )
    op.create_index(op.f("ix_alert_ticket_id"), "alert", ["ticket_id"], unique=True)

    ## actionlog table
    _delete_actionlog()
    op.drop_constraint("actionlog_pteam_id_fkey", "actionlog", type_="foreignkey")
    op.create_foreign_key(
        "actionlog_pteam_id_fkey",
        "actionlog",
        "pteam",
        ["pteam_id"],
        ["pteam_id"],
        ondelete="CASCADE",
    )
    op.add_column("actionlog", sa.Column("service_id", sa.String(length=36), nullable=True))
    op.create_index(op.f("ix_actionlog_service_id"), "actionlog", ["service_id"], unique=False)
    op.create_foreign_key(
        "ix_actionlog_service_id",
        "actionlog",
        "service",
        ["service_id"],
        ["service_id"],
        ondelete="SET NULL",
    )
    op.add_column("actionlog", sa.Column("ticket_id", sa.String(length=36), nullable=True))
    op.create_index(op.f("ix_actionlog_ticket_id"), "actionlog", ["ticket_id"], unique=False)
    op.create_foreign_key(
        "ix_actionlog_ticket_id",
        "actionlog",
        "ticket",
        ["ticket_id"],
        ["ticket_id"],
        ondelete="SET NULL",
    )

    ## delete currentpteamtopictagstatus table
    op.drop_index("ix_currentpteamtopictagstatus_pteam_id", table_name="currentpteamtopictagstatus")
    op.drop_index(
        "ix_currentpteamtopictagstatus_status_id", table_name="currentpteamtopictagstatus"
    )
    op.drop_index("ix_currentpteamtopictagstatus_tag_id", table_name="currentpteamtopictagstatus")
    op.drop_index("ix_currentpteamtopictagstatus_topic_id", table_name="currentpteamtopictagstatus")
    op.drop_table("currentpteamtopictagstatus")

    ## delete pteamtopictagstatus table
    op.drop_index("ix_pteamtopictagstatus_pteam_id", table_name="pteamtopictagstatus")
    op.drop_index("ix_pteamtopictagstatus_tag_id", table_name="pteamtopictagstatus")
    op.drop_index("ix_pteamtopictagstatus_topic_id", table_name="pteamtopictagstatus")
    op.drop_index("ix_pteamtopictagstatus_user_id", table_name="pteamtopictagstatus")
    op.drop_table("pteamtopictagstatus")

    ## delete disabled
    _delete_pteam_disabled()
    _delete_topic_disabled()
    op.drop_column("pteam", "disabled")
    op.drop_column("topic", "disabled")

    ## add CASCADE
    op.drop_constraint("ateampteam_pteam_id_fkey", "ateampteam", type_="foreignkey")
    op.create_foreign_key(
        "ateampteam_pteam_id_fkey",
        "ateampteam",
        "pteam",
        ["pteam_id"],
        ["pteam_id"],
        ondelete="CASCADE",
    )
    op.drop_constraint("pteamaccount_pteam_id_fkey", "pteamaccount", type_="foreignkey")
    op.create_foreign_key(
        "pteamaccount_pteam_id_fkey",
        "pteamaccount",
        "pteam",
        ["pteam_id"],
        ["pteam_id"],
        ondelete="CASCADE",
    )
    op.drop_constraint("pteamauthority_pteam_id_fkey", "pteamauthority", type_="foreignkey")
    op.create_foreign_key(
        "pteamauthority_pteam_id_fkey",
        "pteamauthority",
        "pteam",
        ["pteam_id"],
        ["pteam_id"],
        ondelete="CASCADE",
    )
    op.drop_constraint("pteaminvitation_pteam_id_fkey", "pteaminvitation", type_="foreignkey")
    op.create_foreign_key(
        "pteaminvitation_pteam_id_fkey",
        "pteaminvitation",
        "pteam",
        ["pteam_id"],
        ["pteam_id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    ## delete CASCADE
    op.drop_constraint("pteaminvitation_pteam_id_fkey", "pteaminvitation", type_="foreignkey")
    op.create_foreign_key(
        "pteaminvitation_pteam_id_fkey", "pteaminvitation", "pteam", ["pteam_id"], ["pteam_id"]
    )
    op.drop_constraint("pteamauthority_pteam_id_fkey", "pteamauthority", type_="foreignkey")
    op.create_foreign_key(
        "pteamauthority_pteam_id_fkey", "pteamauthority", "pteam", ["pteam_id"], ["pteam_id"]
    )
    op.drop_constraint("pteamaccount_pteam_id_fkey", "pteamaccount", type_="foreignkey")
    op.create_foreign_key(
        "pteamaccount_pteam_id_fkey", "pteamaccount", "pteam", ["pteam_id"], ["pteam_id"]
    )
    op.drop_constraint("ateampteam_pteam_id_fkey", "ateampteam", type_="foreignkey")
    op.create_foreign_key(
        "ateampteam_pteam_id_fkey", "ateampteam", "pteam", ["pteam_id"], ["pteam_id"]
    )

    ## create disabled
    op.add_column(
        "topic",
        sa.Column(
            "disabled",
            sa.BOOLEAN(),
            server_default=sa.text("FALSE"),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.alter_column("topic", "disabled", server_default=None)
    op.add_column(
        "pteam",
        sa.Column(
            "disabled",
            sa.BOOLEAN(),
            server_default=sa.text("FALSE"),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.alter_column("pteam", "disabled", server_default=None)

    ## create pteamtopictagstatus table
    op.create_table(
        "pteamtopictagstatus",
        sa.Column("status_id", sa.VARCHAR(length=36), autoincrement=False, nullable=False),
        sa.Column("pteam_id", sa.VARCHAR(length=36), autoincrement=False, nullable=False),
        sa.Column("topic_id", sa.VARCHAR(length=36), autoincrement=False, nullable=False),
        sa.Column("tag_id", sa.VARCHAR(length=36), autoincrement=False, nullable=False),
        sa.Column("user_id", sa.VARCHAR(length=36), autoincrement=False, nullable=False),
        sa.Column("note", sa.TEXT(), autoincrement=False, nullable=True),
        sa.Column(
            "logging_ids",
            postgresql.ARRAY(sa.VARCHAR(length=36)),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "assignees",
            postgresql.ARRAY(sa.VARCHAR(length=36)),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column("scheduled_at", postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            autoincrement=False,
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["pteam_id"],
            ["pteam.pteam_id"],
            name="pteamtopictagstatus_pteam_id_fkey",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["tag_id"], ["tag.tag_id"], name="pteamtopictagstatus_tag_id_fkey"),
        sa.ForeignKeyConstraint(
            ["topic_id"],
            ["topic.topic_id"],
            name="pteamtopictagstatus_topic_id_fkey",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["account.user_id"], name="pteamtopictagstatus_user_id_fkey"
        ),
        sa.PrimaryKeyConstraint("status_id", name="pteamtopictagstatus_pkey"),
    )
    op.add_column(
        "pteamtopictagstatus",
        sa.Column(
            "topic_status",
            type_=sa.Enum(name="topicstatustype"),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.create_index(
        "ix_pteamtopictagstatus_user_id", "pteamtopictagstatus", ["user_id"], unique=False
    )
    op.create_index(
        "ix_pteamtopictagstatus_topic_id", "pteamtopictagstatus", ["topic_id"], unique=False
    )
    op.create_index(
        "ix_pteamtopictagstatus_tag_id", "pteamtopictagstatus", ["tag_id"], unique=False
    )
    op.create_index(
        "ix_pteamtopictagstatus_pteam_id", "pteamtopictagstatus", ["pteam_id"], unique=False
    )

    ## create currentpteamtopictagstatus table
    op.create_table(
        "currentpteamtopictagstatus",
        sa.Column("pteam_id", sa.VARCHAR(length=36), autoincrement=False, nullable=False),
        sa.Column("topic_id", sa.VARCHAR(length=36), autoincrement=False, nullable=False),
        sa.Column("tag_id", sa.VARCHAR(length=36), autoincrement=False, nullable=False),
        sa.Column("status_id", sa.VARCHAR(length=36), autoincrement=False, nullable=True),
        sa.Column("threat_impact", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column("updated_at", postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(
            ["pteam_id"],
            ["pteam.pteam_id"],
            name="currentpteamtopictagstatus_pteam_id_fkey",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["status_id"],
            ["pteamtopictagstatus.status_id"],
            name="currentpteamtopictagstatus_status_id_fkey",
        ),
        sa.ForeignKeyConstraint(
            ["tag_id"], ["tag.tag_id"], name="currentpteamtopictagstatus_tag_id_fkey"
        ),
        sa.ForeignKeyConstraint(
            ["topic_id"],
            ["topic.topic_id"],
            name="currentpteamtopictagstatus_topic_id_fkey",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "pteam_id", "topic_id", "tag_id", name="currentpteamtopictagstatus_pkey"
        ),
    )
    op.add_column(
        "currentpteamtopictagstatus",
        sa.Column(
            "topic_status",
            type_=sa.Enum(name="topicstatustype"),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.create_index(
        "ix_currentpteamtopictagstatus_topic_id",
        "currentpteamtopictagstatus",
        ["topic_id"],
        unique=False,
    )
    op.create_index(
        "ix_currentpteamtopictagstatus_tag_id",
        "currentpteamtopictagstatus",
        ["tag_id"],
        unique=False,
    )
    op.create_index(
        "ix_currentpteamtopictagstatus_status_id",
        "currentpteamtopictagstatus",
        ["status_id"],
        unique=False,
    )
    op.create_index(
        "ix_currentpteamtopictagstatus_pteam_id",
        "currentpteamtopictagstatus",
        ["pteam_id"],
        unique=False,
    )

    ## actionlog table
    op.drop_constraint("ix_actionlog_ticket_id", "actionlog", type_="foreignkey")
    op.drop_index(op.f("ix_actionlog_ticket_id"), table_name="actionlog")
    op.drop_column("actionlog", "ticket_id")
    op.drop_constraint("ix_actionlog_service_id", "actionlog", type_="foreignkey")
    op.drop_index(op.f("ix_actionlog_service_id"), table_name="actionlog")
    op.drop_column("actionlog", "service_id")
    op.drop_constraint("actionlog_pteam_id_fkey", "actionlog", type_="foreignkey")
    op.create_foreign_key(
        "actionlog_pteam_id_fkey", "actionlog", "pteam", ["pteam_id"], ["pteam_id"]
    )

    ## delete alert table
    op.drop_index(op.f("ix_alert_ticket_id"), table_name="alert")
    op.drop_table("alert")

    ## delete currentticketstatus table
    op.drop_index(op.f("ix_currentticketstatus_ticket_id"), table_name="currentticketstatus")
    op.drop_index(op.f("ix_currentticketstatus_status_id"), table_name="currentticketstatus")
    op.drop_table("currentticketstatus")

    ## delete ticketstatus table
    op.drop_index(op.f("ix_ticketstatus_user_id"), table_name="ticketstatus")
    op.drop_index(op.f("ix_ticketstatus_ticket_id"), table_name="ticketstatus")
    op.drop_table("ticketstatus")

    ## delete ticket table
    op.drop_index(op.f("ix_ticket_threat_id"), table_name="ticket")
    op.drop_table("ticket")

    ## delete threat table
    op.drop_index(op.f("ix_threat_topic_id"), table_name="threat")
    op.drop_index(op.f("ix_threat_dependency_id"), table_name="threat")
    op.drop_table("threat")

    ## dependency table
    op.drop_constraint(
        "dependency_service_id_tag_id_version_target_key", "dependency", type_="unique"
    )
    op.drop_constraint("dependency_pkey", "dependency", type_="primary")
    op.create_primary_key(
        "dependency_pkey", "dependency", ["service_id", "tag_id", "version", "target"]
    )
    op.drop_column("dependency", "dependency_id")
    op.drop_column("dependency", "dependency_mission_impact")

    ## service table
    op.drop_column("service", "service_mission_impact")
    op.drop_column("service", "exposure")

    ## topic table
    op.drop_column("topic", "automatable")
    op.drop_column("topic", "exploitation")
    op.drop_column("topic", "safety_impact")

    ## delete Enum
    connection = op.get_bind()
    sa.Enum(name="ssvcdeployerpriorityenum").drop(connection)
    sa.Enum(name="missionimpactenum").drop(connection)
    sa.Enum(name="exposureenum").drop(connection)
    sa.Enum(name="safetyimpactenum").drop(connection)
    sa.Enum(name="exploitationenum").drop(connection)
