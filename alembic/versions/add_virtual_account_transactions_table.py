"""add virtual_account_transactions table

Revision ID: add_virtual_account_transactions_table
Revises: add_virtual_accounts_table
Create Date: 2024-12-19 10:01:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_virtual_account_transactions_table'
down_revision = 'add_virtual_accounts_table'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create virtual_account_transactions table
    op.create_table('virtual_account_transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('virtual_account_id', sa.Integer(), nullable=False),
        sa.Column('transaction_type', postgresql.ENUM('credit', 'debit', name='transactiontype'), nullable=False),
        sa.Column('amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('status', postgresql.ENUM('pending', 'completed', 'failed', 'cancelled', name='transactionstatus'), nullable=False),
        sa.Column('indicator', postgresql.ENUM('credit', 'debit', name='transactionindicator'), nullable=False),
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


def downgrade() -> None:
    op.drop_index(op.f('ix_virtual_account_transactions_virtual_account_id'), table_name='virtual_account_transactions')
    op.drop_index(op.f('ix_virtual_account_transactions_id'), table_name='virtual_account_transactions')
    op.drop_table('virtual_account_transactions')
    # Drop the enums
    op.execute('DROP TYPE IF EXISTS transactiontype')
    op.execute('DROP TYPE IF EXISTS transactionstatus')
    op.execute('DROP TYPE IF EXISTS transactionindicator')
