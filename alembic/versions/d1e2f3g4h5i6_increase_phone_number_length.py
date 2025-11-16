"""increase_phone_number_length

Revision ID: d1e2f3g4h5i6
Revises: create_vat_enums
Create Date: 2025-11-16 21:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'd1e2f3g4h5i6'
down_revision: Union[str, None] = 'create_vat_enums'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Increase phone_number column length from 20 to 50 characters
    op.alter_column('users', 'phone_number',
                   existing_type=sa.String(20),
                   type_=sa.String(50),
                   nullable=True)

def downgrade() -> None:
    # Revert phone_number column length back to 20 characters
    op.alter_column('users', 'phone_number',
                   existing_type=sa.String(50),
                   type_=sa.String(20),
                   nullable=True)
