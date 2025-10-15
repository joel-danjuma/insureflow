"""add virtual_accounts table

Revision ID: add_virtual_accounts_table
Revises: 9a8b7c6d5e4f
Create Date: 2024-12-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_virtual_accounts_table'
down_revision = '9a8b7c6d5e4f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create virtual_accounts table
    op.create_table('virtual_accounts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('customer_identifier', sa.String(length=100), nullable=False),
        sa.Column('virtual_account_number', sa.String(length=20), nullable=False),
        sa.Column('bank_code', sa.String(length=10), nullable=False),
        sa.Column('account_type', postgresql.ENUM('individual', 'business', name='virtualaccounttype'), nullable=False),
        sa.Column('status', postgresql.ENUM('active', 'inactive', 'suspended', 'closed', name='virtualaccountstatus'), nullable=False),
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


def downgrade() -> None:
    op.drop_index(op.f('ix_virtual_accounts_virtual_account_number'), table_name='virtual_accounts')
    op.drop_index(op.f('ix_virtual_accounts_customer_identifier'), table_name='virtual_accounts')
    op.drop_index(op.f('ix_virtual_accounts_user_id'), table_name='virtual_accounts')
    op.drop_index(op.f('ix_virtual_accounts_id'), table_name='virtual_accounts')
    op.drop_table('virtual_accounts')
    # Drop the enums
    op.execute('DROP TYPE IF EXISTS virtualaccounttype')
    op.execute('DROP TYPE IF EXISTS virtualaccountstatus')
