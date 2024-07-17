"""Add Mail Tables

Revision ID: 982664e26b3d
Revises: d70c6355860e
Create Date: 2024-02-26 04:05:16.935403

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.engine import Connection

# revision identifiers, used by Alembic.
revision = "982664e26b3d"
down_revision = "d70c6355860e"
branch_labels = None
depends_on = None


def insert_rows_into_ateam_mail(connection: Connection):
    query = """
        INSERT INTO ateammail (ateam_id, enable, address)
          SELECT ateam_id, true, '' FROM ateam
        """
    connection.exec_driver_sql(query)


def insert_rows_into_pteam_mail(connection: Connection):
    query = """
        INSERT INTO pteammail (pteam_id, enable, address)
          SELECT pteam_id, true, '' FROM pteam
        """
    connection.exec_driver_sql(query)


def upgrade() -> None:
    op.create_table(
        "ateammail",
        sa.Column("ateam_id", sa.String(length=36), nullable=False),
        sa.Column("enable", sa.Boolean(), nullable=False),
        sa.Column("address", sa.String(length=255), nullable=False),
        sa.ForeignKeyConstraint(["ateam_id"], ["ateam.ateam_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("ateam_id"),
    )
    op.create_index(op.f("ix_ateammail_ateam_id"), "ateammail", ["ateam_id"], unique=False)
    op.create_table(
        "pteammail",
        sa.Column("pteam_id", sa.String(length=36), nullable=False),
        sa.Column("enable", sa.Boolean(), nullable=False),
        sa.Column("address", sa.String(length=255), nullable=False),
        sa.ForeignKeyConstraint(["pteam_id"], ["pteam.pteam_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("pteam_id"),
    )
    op.create_index(op.f("ix_pteammail_pteam_id"), "pteammail", ["pteam_id"], unique=False)

    connection = op.get_bind()
    insert_rows_into_ateam_mail(connection)
    insert_rows_into_pteam_mail(connection)


def downgrade() -> None:
    op.drop_index(op.f("ix_pteammail_pteam_id"), table_name="pteammail")
    op.drop_table("pteammail")
    op.drop_index(op.f("ix_ateammail_ateam_id"), table_name="ateammail")
    op.drop_table("ateammail")
