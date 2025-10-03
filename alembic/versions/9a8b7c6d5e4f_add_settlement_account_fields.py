"""add settlement account fields to insurance companies

Revision ID: 9a8b7c6d5e4f
Revises: 8f9a0b1c2d3e
Create Date: 2024-10-03 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9a8b7c6d5e4f'
down_revision = '8f9a0b1c2d3e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add settlement account fields to insurance_companies table"""
    
    # Check if columns already exist before adding them
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    # Check if insurance_companies table exists
    tables = inspector.get_table_names()
    if 'insurance_companies' not in tables:
        # Create insurance_companies table if it doesn't exist
        op.create_table(
            'insurance_companies',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=255), nullable=False),
            sa.Column('registration_number', sa.String(length=100), nullable=False),
            sa.Column('address', sa.Text(), nullable=True),
            sa.Column('contact_email', sa.String(length=255), nullable=False),
            sa.Column('contact_phone', sa.String(length=50), nullable=True),
            sa.Column('website', sa.String(length=255), nullable=True),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_insurance_companies_id'), 'insurance_companies', ['id'], unique=False)
        op.create_index(op.f('ix_insurance_companies_name'), 'insurance_companies', ['name'], unique=True)
        op.create_index(op.f('ix_insurance_companies_registration_number'), 'insurance_companies', ['registration_number'], unique=True)
    
    # Get existing columns
    columns = [col['name'] for col in inspector.get_columns('insurance_companies')]
    
    # Add settlement account fields if they don't exist
    if 'settlement_account_number' not in columns:
        op.add_column('insurance_companies', sa.Column('settlement_account_number', sa.String(length=20), nullable=True))
        op.create_index(op.f('ix_insurance_companies_settlement_account_number'), 'insurance_companies', ['settlement_account_number'], unique=False)
    
    if 'settlement_bank_code' not in columns:
        op.add_column('insurance_companies', sa.Column('settlement_bank_code', sa.String(length=10), nullable=True))
    
    if 'settlement_account_name' not in columns:
        op.add_column('insurance_companies', sa.Column('settlement_account_name', sa.String(length=255), nullable=True))


def downgrade() -> None:
    """Remove settlement account fields from insurance_companies table"""
    
    # Remove settlement account fields
    op.drop_index(op.f('ix_insurance_companies_settlement_account_number'), table_name='insurance_companies')
    op.drop_column('insurance_companies', 'settlement_account_name')
    op.drop_column('insurance_companies', 'settlement_bank_code')
    op.drop_column('insurance_companies', 'settlement_account_number')
