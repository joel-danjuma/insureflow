"""add policy_premium to virtual_account_transactions

Revision ID: b2c3d4e5f6g7
Revises: a1b2c3d4e5f6
Create Date: 2025-11-12 19:50:57.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b2c3d4e5f6g7'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add policy_id and premium_id columns to virtual_account_transactions table"""
    # Add policy_id column
    op.add_column('virtual_account_transactions', 
        sa.Column('policy_id', sa.Integer(), nullable=True))
    
    # Add premium_id column
    op.add_column('virtual_account_transactions', 
        sa.Column('premium_id', sa.Integer(), nullable=True))
    
    # Create indexes for both columns
    op.create_index(op.f('ix_virtual_account_transactions_policy_id'), 
        'virtual_account_transactions', ['policy_id'], unique=False)
    op.create_index(op.f('ix_virtual_account_transactions_premium_id'), 
        'virtual_account_transactions', ['premium_id'], unique=False)
    
    # Add foreign key constraints
    op.create_foreign_key('fk_vat_policy_id', 'virtual_account_transactions', 
        'policies', ['policy_id'], ['id'])
    op.create_foreign_key('fk_vat_premium_id', 'virtual_account_transactions', 
        'premiums', ['premium_id'], ['id'])


def downgrade() -> None:
    """Remove policy_id and premium_id columns from virtual_account_transactions table"""
    # Drop foreign key constraints
    op.drop_constraint('fk_vat_premium_id', 'virtual_account_transactions', type_='foreignkey')
    op.drop_constraint('fk_vat_policy_id', 'virtual_account_transactions', type_='foreignkey')
    
    # Drop indexes
    op.drop_index(op.f('ix_virtual_account_transactions_premium_id'), table_name='virtual_account_transactions')
    op.drop_index(op.f('ix_virtual_account_transactions_policy_id'), table_name='virtual_account_transactions')
    
    # Drop columns
    op.drop_column('virtual_account_transactions', 'premium_id')
    op.drop_column('virtual_account_transactions', 'policy_id')

