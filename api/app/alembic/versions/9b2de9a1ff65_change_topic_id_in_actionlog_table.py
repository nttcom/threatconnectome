"""change topic_id in actionlog table

Revision ID: 9b2de9a1ff65
Revises: f4c2c7eb4fc7
Create Date: 2025-04-17 01:19:14.282780

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.engine import Connection

# revision identifiers, used by Alembic.
revision = "9b2de9a1ff65"
down_revision = "f4c2c7eb4fc7"
branch_labels = None
depends_on = None


def delete_actionlog(connection: Connection):
    query = "DELETE FROM actionlog"
    connection.exec_driver_sql(query)


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    connection = op.get_bind()
    delete_actionlog(connection)
    op.add_column("actionlog", sa.Column("vuln_id", sa.String(length=36), nullable=False))
    op.drop_column("actionlog", "topic_id")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    connection = op.get_bind()
    delete_actionlog(connection)
    op.add_column(
        "actionlog",
        sa.Column("topic_id", sa.VARCHAR(length=36), autoincrement=False, nullable=False),
    )
    op.drop_column("actionlog", "vuln_id")
    # ### end Alembic commands ###
