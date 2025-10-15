"""add virtual_accounts_tables

Revision ID: a1b2c3d4e5f6
Revises: add_insureflow_admin_enum
Create Date: 2024-12-19 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = 'add_insureflow_admin_enum'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enums if they don't exist
    conn = op.get_bind()
    
    # Check and create virtualaccounttype enum
    result = conn.execute(text("SELECT 1 FROM pg_type WHERE typname = 'virtualaccounttype'"))
    if not result.fetchone():
        op.execute("CREATE TYPE virtualaccounttype AS ENUM ('individual', 'business')")
    
    # Check and create virtualaccountstatus enum
    result = conn.execute(text("SELECT 1 FROM pg_type WHERE typname = 'virtualaccountstatus'"))
    if not result.fetchone():
        op.execute("CREATE TYPE virtualaccountstatus AS ENUM ('active', 'inactive', 'suspended', 'closed')")
    
    # Check and create transactiontype enum
    result = conn.execute(text("SELECT 1 FROM pg_type WHERE typname = 'transactiontype'"))
    if not result.fetchone():
        op.execute("CREATE TYPE transactiontype AS ENUM ('credit', 'debit')")
    
    # Check and create transactionstatus enum
    result = conn.execute(text("SELECT 1 FROM pg_type WHERE typname = 'transactionstatus'"))
    if not result.fetchone():
        op.execute("CREATE TYPE transactionstatus AS ENUM ('pending', 'completed', 'failed', 'cancelled')")
    
    # Check and create transactionindicator enum
    result = conn.execute(text("SELECT 1 FROM pg_type WHERE typname = 'transactionindicator'"))
    if not result.fetchone():
        op.execute("CREATE TYPE transactionindicator AS ENUM ('credit', 'debit')")

    # Create virtual_accounts table with string columns first
    op.create_table('virtual_accounts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('customer_identifier', sa.String(length=100), nullable=False),
        sa.Column('virtual_account_number', sa.String(length=20), nullable=False),
        sa.Column('bank_code', sa.String(length=10), nullable=False),
        sa.Column('account_type', sa.String(length=20), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=True),
        sa.Column('last_name', sa.String(length=100), nullable=True),
        sa.Column('middle_name', sa.String(length=100), nullable=True),
        sa.Column('bvn', sa.String(length=11), nullable=True),
        sa.Column('date_of_birth', sa.String(length=20), nullable=True),
        sa.Column('gender', sa.String(length=1), nullable=True),
        sa.Column('business_name', sa.String(length=255), nullable=True),
        sa.Column('mobile_number', sa.String(length=20), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('total_credits', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('total_debits', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('current_balance', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('beneficiary_account', sa.String(length=50), nullable=True),
        sa.Column('squad_created_at', sa.DateTime(), nullable=True),
        sa.Column('squad_updated_at', sa.DateTime(), nullable=True),
        sa.Column('platform_commission_rate', sa.Numeric(precision=5, scale=4), nullable=False),
        sa.Column('insureflow_commission_rate', sa.Numeric(precision=5, scale=4), nullable=False),
        sa.Column('habari_commission_rate', sa.Numeric(precision=5, scale=4), nullable=False),
        sa.Column('auto_settlement', sa.Boolean(), nullable=False),
        sa.Column('settlement_threshold', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('last_activity_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_virtual_accounts_id'), 'virtual_accounts', ['id'], unique=False)
    op.create_index(op.f('ix_virtual_accounts_user_id'), 'virtual_accounts', ['user_id'], unique=False)
    op.create_index(op.f('ix_virtual_accounts_customer_identifier'), 'virtual_accounts', ['customer_identifier'], unique=True)
    op.create_index(op.f('ix_virtual_accounts_virtual_account_number'), 'virtual_accounts', ['virtual_account_number'], unique=True)

    # Create virtual_account_transactions table with string columns first
    op.create_table('virtual_account_transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('virtual_account_id', sa.Integer(), nullable=False),
        sa.Column('transaction_type', sa.String(length=20), nullable=False),
        sa.Column('amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('indicator', sa.String(length=20), nullable=False),
        sa.Column('reference', sa.String(length=100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('squad_transaction_id', sa.String(length=100), nullable=True),
        sa.Column('squad_reference', sa.String(length=100), nullable=True),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['virtual_account_id'], ['virtual_accounts.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_virtual_account_transactions_id'), 'virtual_account_transactions', ['id'], unique=False)
    op.create_index(op.f('ix_virtual_account_transactions_virtual_account_id'), 'virtual_account_transactions', ['virtual_account_id'], unique=False)

    # Now alter the columns to use enum types with explicit casting
    op.execute("ALTER TABLE virtual_accounts ALTER COLUMN account_type TYPE virtualaccounttype USING account_type::virtualaccounttype")
    op.execute("ALTER TABLE virtual_accounts ALTER COLUMN status TYPE virtualaccountstatus USING status::virtualaccountstatus")
    op.execute("ALTER TABLE virtual_account_transactions ALTER COLUMN transaction_type TYPE transactiontype USING transaction_type::transactiontype")
    op.execute("ALTER TABLE virtual_account_transactions ALTER COLUMN status TYPE transactionstatus USING status::transactionstatus")
    op.execute("ALTER TABLE virtual_account_transactions ALTER COLUMN indicator TYPE transactionindicator USING indicator::transactionindicator")


def downgrade() -> None:
    op.drop_index(op.f('ix_virtual_account_transactions_virtual_account_id'), table_name='virtual_account_transactions')
    op.drop_index(op.f('ix_virtual_account_transactions_id'), table_name='virtual_account_transactions')
    op.drop_table('virtual_account_transactions')
    op.drop_index(op.f('ix_virtual_accounts_virtual_account_number'), table_name='virtual_accounts')
    op.drop_index(op.f('ix_virtual_accounts_customer_identifier'), table_name='virtual_accounts')
    op.drop_index(op.f('ix_virtual_accounts_user_id'), table_name='virtual_accounts')
    op.drop_index(op.f('ix_virtual_accounts_id'), table_name='virtual_accounts')
    op.drop_table('virtual_accounts')
    # Drop the enums
    op.execute('DROP TYPE IF EXISTS virtualaccounttype')
    op.execute('DROP TYPE IF EXISTS virtualaccountstatus')
    op.execute('DROP TYPE IF EXISTS transactiontype')
    op.execute('DROP TYPE IF EXISTS transactionstatus')
    op.execute('DROP TYPE IF EXISTS transactionindicator')
