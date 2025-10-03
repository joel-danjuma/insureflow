"""add_missing_user_profile_fields

Revision ID: 6f312bf7ddad
Revises: 2a3b4c5d6e7f
Create Date: 2025-10-03 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6f312bf7ddad'
down_revision: Union[str, None] = '2a3b4c5d6e7f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Check if columns exist before adding them (idempotent migration)
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('users')]
    
    # Add phone_number if it doesn't exist
    if 'phone_number' not in columns:
        op.add_column('users', sa.Column('phone_number', sa.String(length=20), nullable=True))
    
    # Add organization_name if it doesn't exist
    if 'organization_name' not in columns:
        op.add_column('users', sa.Column('organization_name', sa.String(length=255), nullable=True))
    
    # Add bvn if it doesn't exist
    if 'bvn' not in columns:
        op.add_column('users', sa.Column('bvn', sa.String(length=11), nullable=True))
    
    # Add date_of_birth if it doesn't exist
    if 'date_of_birth' not in columns:
        op.add_column('users', sa.Column('date_of_birth', sa.DateTime(), nullable=True))
    
    # Add gender if it doesn't exist
    if 'gender' not in columns:
        op.add_column('users', sa.Column('gender', sa.String(length=10), nullable=True))
    
    # Add address if it doesn't exist
    if 'address' not in columns:
        op.add_column('users', sa.Column('address', sa.String(length=500), nullable=True))
    
    # Add can_create_policies if it doesn't exist
    if 'can_create_policies' not in columns:
        op.add_column('users', sa.Column('can_create_policies', sa.Boolean(), nullable=False, server_default='false'))
    
    # Add can_make_payments if it doesn't exist
    if 'can_make_payments' not in columns:
        op.add_column('users', sa.Column('can_make_payments', sa.Boolean(), nullable=False, server_default='false'))


def downgrade() -> None:
    # Remove the added columns
    op.drop_column('users', 'can_make_payments')
    op.drop_column('users', 'can_create_policies')
    op.drop_column('users', 'address')
    op.drop_column('users', 'gender')
    op.drop_column('users', 'date_of_birth')
    op.drop_column('users', 'bvn')
    op.drop_column('users', 'organization_name')
    op.drop_column('users', 'phone_number')
