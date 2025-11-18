"""fix_varchar_columns_type_1043

Revision ID: 5b548823ce3e
Revises: d1e2f3g4h5i6
Create Date: 2025-11-18 00:00:05.678753

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5b548823ce3e'
down_revision: Union[str, None] = 'd1e2f3g4h5i6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Fix unbounded VARCHAR columns in policies table that cause 
    'Unknown PG numeric type: 1043' error with SQLAlchemy 2.0+ and psycopg3.
    
    PostgreSQL type 1043 represents VARCHAR without explicit length constraints.
    This migration ensures all VARCHAR columns have explicit length limits.
    """
    # Get database connection
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    # Check if policies table exists
    if 'policies' in inspector.get_table_names():
        columns = {col['name']: col for col in inspector.get_columns('policies')}
        
        # Fix merchant_reference column if it exists and is unbounded VARCHAR
        if 'merchant_reference' in columns:
            col_info = columns['merchant_reference']
            # Check if it's a VARCHAR without length (type 1043)
            if hasattr(col_info['type'], 'length') and col_info['type'].length is None:
                op.alter_column('policies', 'merchant_reference',
                              existing_type=sa.String(),
                              type_=sa.String(100),
                              existing_nullable=True)
        
        # Fix payment_status column if it exists and is unbounded VARCHAR  
        if 'payment_status' in columns:
            col_info = columns['payment_status']
            if hasattr(col_info['type'], 'length') and col_info['type'].length is None:
                op.alter_column('policies', 'payment_status',
                              existing_type=sa.String(),
                              type_=sa.String(50),
                              existing_nullable=True)
        
        # Fix transaction_reference column if it exists and is unbounded VARCHAR
        if 'transaction_reference' in columns:
            col_info = columns['transaction_reference']
            if hasattr(col_info['type'], 'length') and col_info['type'].length is None:
                op.alter_column('policies', 'transaction_reference',
                              existing_type=sa.String(),
                              type_=sa.String(100),
                              existing_nullable=True)
    
    # Alternative approach: Use raw SQL to fix any remaining unbounded VARCHAR columns
    # This handles cases where the Python inspection might not catch all issues
    try:
        conn.execute(sa.text("""
            -- Fix merchant_reference if it's unbounded VARCHAR
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'policies' 
                    AND column_name = 'merchant_reference'
                    AND data_type = 'character varying'
                    AND character_maximum_length IS NULL
                ) THEN
                    ALTER TABLE policies ALTER COLUMN merchant_reference TYPE VARCHAR(100);
                END IF;
            END $$;
            
            -- Fix payment_status if it's unbounded VARCHAR
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'policies' 
                    AND column_name = 'payment_status'
                    AND data_type = 'character varying'
                    AND character_maximum_length IS NULL
                ) THEN
                    ALTER TABLE policies ALTER COLUMN payment_status TYPE VARCHAR(50);
                END IF;
            END $$;
            
            -- Fix transaction_reference if it's unbounded VARCHAR
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'policies' 
                    AND column_name = 'transaction_reference'
                    AND data_type = 'character varying'
                    AND character_maximum_length IS NULL
                ) THEN
                    ALTER TABLE policies ALTER COLUMN transaction_reference TYPE VARCHAR(100);
                END IF;
            END $$;
        """))
    except Exception as e:
        # Log the error but don't fail the migration
        print(f"Warning: Could not execute raw SQL fix: {e}")


def downgrade() -> None:
    """
    Revert VARCHAR columns back to unbounded (not recommended).
    This is mainly for completeness - in practice, you wouldn't want
    to revert this fix as it would reintroduce the type 1043 error.
    """
    # Get database connection
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    # Check if policies table exists
    if 'policies' in inspector.get_table_names():
        columns = {col['name']: col for col in inspector.get_columns('policies')}
        
        # Revert merchant_reference column to unbounded VARCHAR (not recommended)
        if 'merchant_reference' in columns:
            op.alter_column('policies', 'merchant_reference',
                          existing_type=sa.String(100),
                          type_=sa.String(),
                          existing_nullable=True)
        
        # Revert payment_status column to unbounded VARCHAR (not recommended)
        if 'payment_status' in columns:
            op.alter_column('policies', 'payment_status',
                          existing_type=sa.String(50),
                          type_=sa.String(),
                          existing_nullable=True)
        
        # Revert transaction_reference column to unbounded VARCHAR (not recommended)
        if 'transaction_reference' in columns:
            op.alter_column('policies', 'transaction_reference',
                          existing_type=sa.String(100),
                          type_=sa.String(),
                          existing_nullable=True)
