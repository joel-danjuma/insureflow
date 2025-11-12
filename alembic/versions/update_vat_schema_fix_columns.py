"""update virtual_account_transactions schema

Revision ID: update_vat_schema
Revises: 067a88cb2e76
Create Date: 2025-11-12 21:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = 'update_vat_schema'
down_revision = '067a88cb2e76'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Update virtual_account_transactions table to match model schema"""
    conn = op.get_bind()
    
    # Fix transactiontype enum - add missing values
    # The enum might have been created with different values in initial migration
    # We need: 'credit', 'debit', 'commission', 'settlement', 'refund'
    result = conn.execute(text("""
        SELECT enumlabel 
        FROM pg_enum 
        WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'transactiontype')
        ORDER BY enumsortorder
    """))
    existing_values = [row[0] for row in result]
    
    enum_values_to_add = ['credit', 'debit', 'commission', 'settlement', 'refund']
    for value in enum_values_to_add:
        if value not in existing_values:
            try:
                op.execute(f"ALTER TYPE transactiontype ADD VALUE IF NOT EXISTS '{value}'")
            except Exception:
                try:
                    op.execute(f"ALTER TYPE transactiontype ADD VALUE '{value}'")
                except Exception as e:
                    if 'already exists' not in str(e).lower():
                        raise
    
    # Fix transactionstatus enum - add 'reversed' if missing
    result = conn.execute(text("""
        SELECT enumlabel 
        FROM pg_enum 
        WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'transactionstatus')
        ORDER BY enumsortorder
    """))
    existing_status_values = [row[0] for row in result]
    
    if 'reversed' not in existing_status_values:
        try:
            op.execute("ALTER TYPE transactionstatus ADD VALUE IF NOT EXISTS 'reversed'")
        except Exception:
            try:
                op.execute("ALTER TYPE transactionstatus ADD VALUE 'reversed'")
            except Exception as e:
                if 'already exists' not in str(e).lower():
                    raise
    
    # Check if columns exist before renaming
    result = conn.execute(text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'virtual_account_transactions' 
        AND column_name IN ('reference', 'transaction_reference')
    """))
    columns = [row[0] for row in result]
    
    # Rename columns if old names exist
    if 'reference' in columns and 'transaction_reference' not in columns:
        op.execute("ALTER TABLE virtual_account_transactions RENAME COLUMN reference TO transaction_reference")
    
    result = conn.execute(text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'virtual_account_transactions' 
        AND column_name IN ('squad_reference', 'squad_transaction_reference')
    """))
    columns = [row[0] for row in result]
    if 'squad_reference' in columns and 'squad_transaction_reference' not in columns:
        op.execute("ALTER TABLE virtual_account_transactions RENAME COLUMN squad_reference TO squad_transaction_reference")
    
    result = conn.execute(text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'virtual_account_transactions' 
        AND column_name IN ('indicator', 'transaction_indicator')
    """))
    columns = [row[0] for row in result]
    if 'indicator' in columns and 'transaction_indicator' not in columns:
        op.execute("ALTER TABLE virtual_account_transactions RENAME COLUMN indicator TO transaction_indicator")
    
    result = conn.execute(text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'virtual_account_transactions' 
        AND column_name IN ('description', 'remarks')
    """))
    columns = [row[0] for row in result]
    if 'description' in columns and 'remarks' not in columns:
        op.execute("ALTER TABLE virtual_account_transactions RENAME COLUMN description TO remarks")
    
    # Handle amount -> principal_amount + settled_amount
    result = conn.execute(text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'virtual_account_transactions' 
        AND column_name IN ('amount', 'principal_amount')
    """))
    columns = [row[0] for row in result]
    
    if 'amount' in columns and 'principal_amount' not in columns:
        op.execute("ALTER TABLE virtual_account_transactions RENAME COLUMN amount TO principal_amount")
        op.add_column('virtual_account_transactions', sa.Column('settled_amount', sa.Numeric(15, 2), nullable=True))
        op.execute("UPDATE virtual_account_transactions SET settled_amount = principal_amount WHERE settled_amount IS NULL")
        op.alter_column('virtual_account_transactions', 'settled_amount', nullable=False)
    
    # Add all missing columns (using IF NOT EXISTS check)
    result = conn.execute(text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'virtual_account_transactions'
    """))
    existing_columns = [row[0] for row in result]
    
    if 'fee_charged' not in existing_columns:
        op.add_column('virtual_account_transactions', sa.Column('fee_charged', sa.Numeric(10, 2), nullable=False, server_default='0'))
    if 'total_platform_commission' not in existing_columns:
        op.add_column('virtual_account_transactions', sa.Column('total_platform_commission', sa.Numeric(10, 2), nullable=False, server_default='0'))
    if 'insureflow_commission' not in existing_columns:
        op.add_column('virtual_account_transactions', sa.Column('insureflow_commission', sa.Numeric(10, 2), nullable=False, server_default='0'))
    if 'habari_commission' not in existing_columns:
        op.add_column('virtual_account_transactions', sa.Column('habari_commission', sa.Numeric(10, 2), nullable=False, server_default='0'))
    if 'currency' not in existing_columns:
        op.add_column('virtual_account_transactions', sa.Column('currency', sa.String(3), nullable=False, server_default='NGN'))
    if 'channel' not in existing_columns:
        op.add_column('virtual_account_transactions', sa.Column('channel', sa.String(50), nullable=False, server_default='virtual-account'))
    if 'sender_name' not in existing_columns:
        op.add_column('virtual_account_transactions', sa.Column('sender_name', sa.String(255), nullable=True))
    if 'transaction_date' not in existing_columns:
        op.add_column('virtual_account_transactions', sa.Column('transaction_date', sa.DateTime(), nullable=True))
    if 'merchant_settlement_date' not in existing_columns:
        op.add_column('virtual_account_transactions', sa.Column('merchant_settlement_date', sa.DateTime(), nullable=True))
    if 'alerted_merchant' not in existing_columns:
        op.add_column('virtual_account_transactions', sa.Column('alerted_merchant', sa.Boolean(), nullable=False, server_default='false'))
    if 'frozen_transaction' not in existing_columns:
        op.add_column('virtual_account_transactions', sa.Column('frozen_transaction', sa.Boolean(), nullable=False, server_default='false'))
    if 'freeze_transaction_ref' not in existing_columns:
        op.add_column('virtual_account_transactions', sa.Column('freeze_transaction_ref', sa.String(100), nullable=True))
    if 'reason_for_frozen_transaction' not in existing_columns:
        op.add_column('virtual_account_transactions', sa.Column('reason_for_frozen_transaction', sa.Text(), nullable=True))
    if 'webhook_received_at' not in existing_columns:
        op.add_column('virtual_account_transactions', sa.Column('webhook_received_at', sa.DateTime(), nullable=True))
    if 'notification_sent' not in existing_columns:
        op.add_column('virtual_account_transactions', sa.Column('notification_sent', sa.Boolean(), nullable=False, server_default='false'))
    if 'transaction_metadata' not in existing_columns:
        op.add_column('virtual_account_transactions', sa.Column('transaction_metadata', sa.Text(), nullable=True))
    
    # Set transaction_date from processed_at or created_at
    op.execute("""
        UPDATE virtual_account_transactions 
        SET transaction_date = COALESCE(processed_at, created_at) 
        WHERE transaction_date IS NULL
    """)
    
    # Make transaction_date NOT NULL after setting values
    result = conn.execute(text("""
        SELECT column_name, is_nullable
        FROM information_schema.columns 
        WHERE table_name = 'virtual_account_transactions' 
        AND column_name = 'transaction_date'
    """))
    if result.fetchone():
        op.alter_column('virtual_account_transactions', 'transaction_date', nullable=False)
    
    # Create unique index on transaction_reference if it doesn't exist
    result = conn.execute(text("""
        SELECT indexname 
        FROM pg_indexes 
        WHERE tablename = 'virtual_account_transactions' 
        AND indexname = 'ix_virtual_account_transactions_transaction_reference'
    """))
    if not result.fetchone():
        op.create_index('ix_virtual_account_transactions_transaction_reference', 
                        'virtual_account_transactions', ['transaction_reference'], unique=True)


def downgrade() -> None:
    """Revert schema changes"""
    # Note: Full downgrade would require reversing all changes, which is complex
    # For now, we'll just drop the index
    op.drop_index('ix_virtual_account_transactions_transaction_reference', table_name='virtual_account_transactions')
    pass

