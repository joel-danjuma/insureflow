"""Add INSUREFLOW_ADMIN to userrole enum

Revision ID: add_insureflow_admin_enum
Revises: 9a8b7c6d5e4f
Create Date: 2024-12-14 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_insureflow_admin_enum'
down_revision = '9a8b7c6d5e4f'
branch_labels = None
depends_on = None

def upgrade():
    # Add INSUREFLOW_ADMIN to the userrole enum
    op.execute("ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'INSUREFLOW_ADMIN'")

def downgrade():
    # Note: PostgreSQL doesn't support removing enum values easily
    # This would require recreating the enum and updating all references
    pass
