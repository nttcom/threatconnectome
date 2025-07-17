"""change datetime type

Revision ID: a529a44388db
Revises: 4479f2acf45e
Create Date: 2025-06-30 06:16:53.350909

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a529a44388db'
down_revision = '4479f2acf45e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE service ALTER COLUMN sbom_uploaded_at TYPE TIMESTAMP WITH TIME ZONE USING sbom_uploaded_at AT TIME ZONE 'UTC'")
    op.execute("ALTER TABLE ticket ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE USING created_at AT TIME ZONE 'UTC'")
    op.execute("ALTER TABLE ticketstatus ALTER COLUMN scheduled_at TYPE TIMESTAMP WITH TIME ZONE USING scheduled_at AT TIME ZONE 'UTC'")
    op.execute("ALTER TABLE ticketstatus ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE USING created_at AT TIME ZONE 'UTC'")
    op.execute("ALTER TABLE alert ALTER COLUMN alerted_at TYPE TIMESTAMP WITH TIME ZONE USING alerted_at AT TIME ZONE 'UTC'")
    op.execute("ALTER TABLE vuln ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE USING created_at AT TIME ZONE 'UTC'")
    op.execute("ALTER TABLE vuln ALTER COLUMN updated_at TYPE TIMESTAMP WITH TIME ZONE USING updated_at AT TIME ZONE 'UTC'")
    op.execute("ALTER TABLE vulnaction ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE USING created_at AT TIME ZONE 'UTC'")
    op.execute("ALTER TABLE actionlog ALTER COLUMN executed_at TYPE TIMESTAMP WITH TIME ZONE USING executed_at AT TIME ZONE 'UTC'")
    op.execute("ALTER TABLE actionlog ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE USING created_at AT TIME ZONE 'UTC'")
    op.execute("ALTER TABLE pteaminvitation ALTER COLUMN expiration TYPE TIMESTAMP WITH TIME ZONE USING expiration AT TIME ZONE 'UTC'")


def downgrade() -> None:
    op.execute("ALTER TABLE service ALTER COLUMN sbom_uploaded_at TYPE TIMESTAMP WITHOUT TIME ZONE USING sbom_uploaded_at AT TIME ZONE 'UTC'")
    op.execute("ALTER TABLE ticket ALTER COLUMN created_at TYPE TIMESTAMP WITHOUT TIME ZONE USING created_at AT TIME ZONE 'UTC'")
    op.execute("ALTER TABLE ticketstatus ALTER COLUMN scheduled_at TYPE TIMESTAMP WITHOUT TIME ZONE USING scheduled_at AT TIME ZONE 'UTC'")
    op.execute("ALTER TABLE ticketstatus ALTER COLUMN created_at TYPE TIMESTAMP WITHOUT TIME ZONE USING created_at AT TIME ZONE 'UTC'")
    op.execute("ALTER TABLE alert ALTER COLUMN alerted_at TYPE TIMESTAMP WITHOUT TIME ZONE USING alerted_at AT TIME ZONE 'UTC'")
    op.execute("ALTER TABLE vuln ALTER COLUMN created_at TYPE TIMESTAMP WITHOUT TIME ZONE USING created_at AT TIME ZONE 'UTC'")
    op.execute("ALTER TABLE vuln ALTER COLUMN updated_at TYPE TIMESTAMP WITHOUT TIME ZONE USING updated_at AT TIME ZONE 'UTC'")
    op.execute("ALTER TABLE vulnaction ALTER COLUMN created_at TYPE TIMESTAMP WITHOUT TIME ZONE USING created_at AT TIME ZONE 'UTC'")
    op.execute("ALTER TABLE actionlog ALTER COLUMN executed_at TYPE TIMESTAMP WITHOUT TIME ZONE USING executed_at AT TIME ZONE 'UTC'")
    op.execute("ALTER TABLE actionlog ALTER COLUMN created_at TYPE TIMESTAMP WITHOUT TIME ZONE USING created_at AT TIME ZONE 'UTC'")
    op.execute("ALTER TABLE pteaminvitation ALTER COLUMN expiration TYPE TIMESTAMP WITHOUT TIME ZONE USING expiration AT TIME ZONE 'UTC'")
    