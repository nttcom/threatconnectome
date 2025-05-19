"""make_actionlog.action_and_related_columns_nullable

Revision ID: 68d85e0499fe
Revises: 312b1a6f45cf
Create Date: 2025-05-19 14:13:10.178975

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "68d85e0499fe"
down_revision = "b842fabcecf2"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("actionlog", "action", existing_type=sa.Text(), nullable=True)
    op.alter_column("actionlog", "action_type", existing_type=sa.String(length=32), nullable=True)
    op.alter_column("actionlog", "recommended", existing_type=sa.Boolean(), nullable=True)


def downgrade():
    op.alter_column("actionlog", "action", existing_type=sa.Text(), nullable=False)
    op.alter_column("actionlog", "action_type", existing_type=sa.String(length=32), nullable=False)
    op.alter_column("actionlog", "recommended", existing_type=sa.Boolean(), nullable=False)
