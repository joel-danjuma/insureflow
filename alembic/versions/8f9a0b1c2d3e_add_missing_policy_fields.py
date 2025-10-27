"""add_missing_policy_fields

Revision ID: 8f9a0b1c2d3e
Revises: 6f312bf7ddad
Create Date: 2025-10-03 10:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '8f9a0b1c2d3e'
down_revision: Union[str, None] = '6f312bf7ddad'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Check if columns exist before adding them (idempotent migration)
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('policies')]
    
    # Add policy_name if it doesn't exist
    if 'policy_name' not in columns:
        op.add_column('policies', sa.Column('policy_name', sa.String(length=255), nullable=False, server_default='Default Policy'))
    
    # Add due_date if it doesn't exist
    if 'due_date' not in columns:
        op.add_column('policies', sa.Column('due_date', sa.Date(), nullable=False, server_default='2025-12-31'))
    
    # Add duration_months if it doesn't exist
    if 'duration_months' not in columns:
        op.add_column('policies', sa.Column('duration_months', sa.Integer(), nullable=True))
    
    # Add premium_amount if it doesn't exist
    if 'premium_amount' not in columns:
        op.add_column('policies', sa.Column('premium_amount', sa.Numeric(precision=15, scale=2), nullable=False, server_default='0.00'))
    
    # Add payment_frequency if it doesn't exist
    if 'payment_frequency' not in columns:
        # Create enum type if it doesn't exist
        payment_frequency_enum = postgresql.ENUM('MONTHLY', 'QUARTERLY', 'ANNUALLY', 'CUSTOM', name='paymentfrequency')
        payment_frequency_enum.create(conn, checkfirst=True)
        op.add_column('policies', sa.Column('payment_frequency', payment_frequency_enum, nullable=False, server_default='MONTHLY'))
    
    # Add first_payment_date if it doesn't exist
    if 'first_payment_date' not in columns:
        op.add_column('policies', sa.Column('first_payment_date', sa.Date(), nullable=True))
    
    # Add last_payment_date if it doesn't exist
    if 'last_payment_date' not in columns:
        op.add_column('policies', sa.Column('last_payment_date', sa.Date(), nullable=True))
    
    # Add grace_period_days if it doesn't exist
    if 'grace_period_days' not in columns:
        op.add_column('policies', sa.Column('grace_period_days', sa.Integer(), nullable=False, server_default='30'))
    
    # Add custom_payment_schedule if it doesn't exist
    if 'custom_payment_schedule' not in columns:
        op.add_column('policies', sa.Column('custom_payment_schedule', sa.Text(), nullable=True))
    
    # Add company_name if it doesn't exist
    if 'company_name' not in columns:
        op.add_column('policies', sa.Column('company_name', sa.String(length=255), nullable=False, server_default='Default Company'))
    
    # Add contact_person if it doesn't exist
    if 'contact_person' not in columns:
        op.add_column('policies', sa.Column('contact_person', sa.String(length=255), nullable=False, server_default='Default Contact'))
    
    # Add contact_email if it doesn't exist
    if 'contact_email' not in columns:
        op.add_column('policies', sa.Column('contact_email', sa.String(length=255), nullable=False, server_default='contact@example.com'))
    
    # Add contact_phone if it doesn't exist
    if 'contact_phone' not in columns:
        op.add_column('policies', sa.Column('contact_phone', sa.String(length=50), nullable=True))
    
    # Add rc_number if it doesn't exist
    if 'rc_number' not in columns:
        op.add_column('policies', sa.Column('rc_number', sa.String(length=100), nullable=True))
    
    # Add coverage_items if it doesn't exist
    if 'coverage_items' not in columns:
        op.add_column('policies', sa.Column('coverage_items', sa.Text(), nullable=True))
    
    # Add beneficiaries if it doesn't exist
    if 'beneficiaries' not in columns:
        op.add_column('policies', sa.Column('beneficiaries', sa.Text(), nullable=True))
    
    # Add broker_notes if it doesn't exist
    if 'broker_notes' not in columns:
        op.add_column('policies', sa.Column('broker_notes', sa.Text(), nullable=True))
    
    # Add internal_tags if it doesn't exist
    if 'internal_tags' not in columns:
        op.add_column('policies', sa.Column('internal_tags', sa.Text(), nullable=True))
    
    # Add auto_renew if it doesn't exist
    if 'auto_renew' not in columns:
        op.add_column('policies', sa.Column('auto_renew', sa.Boolean(), nullable=False, server_default='false'))
    
    # Add notify_broker_on_change if it doesn't exist
    if 'notify_broker_on_change' not in columns:
        op.add_column('policies', sa.Column('notify_broker_on_change', sa.Boolean(), nullable=False, server_default='true'))
    
    # Add commission_structure if it doesn't exist
    if 'commission_structure' not in columns:
        op.add_column('policies', sa.Column('commission_structure', sa.Text(), nullable=True))
    
    # Add policy_documents if it doesn't exist
    if 'policy_documents' not in columns:
        op.add_column('policies', sa.Column('policy_documents', sa.Text(), nullable=True))
    
    # Add kyc_documents if it doesn't exist
    if 'kyc_documents' not in columns:
        op.add_column('policies', sa.Column('kyc_documents', sa.Text(), nullable=True))
    
    # Add terms_and_conditions if it doesn't exist
    if 'terms_and_conditions' not in columns:
        op.add_column('policies', sa.Column('terms_and_conditions', sa.Text(), nullable=True))
    
    # Add merchant_reference if it doesn't exist
    if 'merchant_reference' not in columns:
        op.add_column('policies', sa.Column('merchant_reference', sa.String(), nullable=True))
        op.create_index('ix_policies_merchant_reference', 'policies', ['merchant_reference'], unique=True)
    
    # Add payment_status if it doesn't exist
    if 'payment_status' not in columns:
        op.add_column('policies', sa.Column('payment_status', sa.String(), nullable=True, server_default='pending'))
    
    # Add transaction_reference if it doesn't exist
    if 'transaction_reference' not in columns:
        op.add_column('policies', sa.Column('transaction_reference', sa.String(), nullable=True))
        op.create_index('ix_policies_transaction_reference', 'policies', ['transaction_reference'], unique=True)


def downgrade() -> None:
    # Remove the added columns and indexes
    op.drop_index('ix_policies_transaction_reference', table_name='policies')
    op.drop_column('policies', 'transaction_reference')
    op.drop_column('policies', 'payment_status')
    op.drop_index('ix_policies_merchant_reference', table_name='policies')
    op.drop_column('policies', 'merchant_reference')
    op.drop_column('policies', 'terms_and_conditions')
    op.drop_column('policies', 'kyc_documents')
    op.drop_column('policies', 'policy_documents')
    op.drop_column('policies', 'commission_structure')
    op.drop_column('policies', 'notify_broker_on_change')
    op.drop_column('policies', 'auto_renew')
    op.drop_column('policies', 'internal_tags')
    op.drop_column('policies', 'broker_notes')
    op.drop_column('policies', 'beneficiaries')
    op.drop_column('policies', 'coverage_items')
    op.drop_column('policies', 'rc_number')
    op.drop_column('policies', 'contact_phone')
    op.drop_column('policies', 'contact_email')
    op.drop_column('policies', 'contact_person')
    op.drop_column('policies', 'company_name')
    op.drop_column('policies', 'custom_payment_schedule')
    op.drop_column('policies', 'grace_period_days')
    op.drop_column('policies', 'last_payment_date')
    op.drop_column('policies', 'first_payment_date')
    op.drop_column('policies', 'payment_frequency')
    op.drop_column('policies', 'premium_amount')
    op.drop_column('policies', 'duration_months')
    op.drop_column('policies', 'due_date')
    op.drop_column('policies', 'policy_name')
    
    # Drop enum type
    payment_frequency_enum = postgresql.ENUM('MONTHLY', 'QUARTERLY', 'ANNUALLY', 'CUSTOM', name='paymentfrequency')
    payment_frequency_enum.drop(op.get_bind(), checkfirst=True)
