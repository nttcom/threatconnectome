"""make_actionlog.action_id__nullable

Revision ID: 62a9068190ec
Revises: b842fabcecf2
Create Date: 2025-05-19 16:22:31.615601

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "62a9068190ec"
down_revision = "b842fabcecf2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("actionlog", "action_id", existing_type=sa.Text(), nullable=True)


def downgrade() -> None:
    op.alter_column("actionlog", "action_id", existing_type=sa.Text(), nullable=False)
