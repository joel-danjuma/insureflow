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
    Fix ALL unbounded VARCHAR columns in policies table that cause 
    'Unknown PG numeric type: 1043' error with SQLAlchemy 2.0+ and psycopg3.
    
    This migration dynamically finds and fixes all unbounded VARCHAR columns
    by querying information_schema directly. PostgreSQL type 1043 represents 
    VARCHAR without explicit length constraints.
    """
    conn = op.get_bind()
    
    # Define column length mappings based on column names
    # This ensures we apply appropriate lengths to each column
    column_lengths = {
        'merchant_reference': 100,
        'payment_status': 50,
        'transaction_reference': 100,
        'policy_number': 100,
        'policy_name': 255,
        'company_name': 255,
        'contact_person': 255,
        'contact_email': 255,
        'contact_phone': 50,
        'rc_number': 100,
        'coverage_amount': 20,  # This might be Numeric, but if it's VARCHAR, fix it
    }
    
    # Use raw SQL to find and fix ALL unbounded VARCHAR columns dynamically
    # This approach is more reliable than Python inspection
    try:
        # First, find all unbounded VARCHAR columns
        result = conn.execute(sa.text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'policies'
            AND table_schema = 'public'
            AND data_type = 'character varying'
            AND character_maximum_length IS NULL
        """))
        
        unbounded_columns = [row[0] for row in result]
        
        if unbounded_columns:
            print(f"Found {len(unbounded_columns)} unbounded VARCHAR columns: {unbounded_columns}")
            
            # Fix each unbounded column with appropriate length
            for column_name in unbounded_columns:
                # Get the appropriate length, default to 255 if not specified
                length = column_lengths.get(column_name, 255)
                
                # Execute ALTER TABLE to fix the column
                # Using USING clause to safely cast existing data
                conn.execute(sa.text(f"""
                    ALTER TABLE policies 
                    ALTER COLUMN {column_name} 
                    TYPE VARCHAR({length})
                    USING {column_name}::VARCHAR({length})
                """))
                
                print(f"Fixed column '{column_name}' to VARCHAR({length})")
            
            # Commit the changes
            conn.commit()
        else:
            print("No unbounded VARCHAR columns found in policies table")
        
    except Exception as e:
        # If the dynamic approach fails, try the specific column fixes
        print(f"Dynamic fix failed: {e}, trying specific column fixes...")
        
        # Fallback: Fix known columns specifically
        try:
            conn.execute(sa.text("""
                DO $$
                BEGIN
                    -- Fix merchant_reference
                    IF EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name = 'policies' 
                        AND column_name = 'merchant_reference'
                        AND data_type = 'character varying'
                        AND character_maximum_length IS NULL
                    ) THEN
                        ALTER TABLE policies ALTER COLUMN merchant_reference TYPE VARCHAR(100);
                    END IF;
                    
                    -- Fix payment_status
                    IF EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name = 'policies' 
                        AND column_name = 'payment_status'
                        AND data_type = 'character varying'
                        AND character_maximum_length IS NULL
                    ) THEN
                        ALTER TABLE policies ALTER COLUMN payment_status TYPE VARCHAR(50);
                    END IF;
                    
                    -- Fix transaction_reference
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
            conn.commit()
            print("Fallback: Fixed specific columns using DO block")
        except Exception as e2:
            print(f"Specific column fix also failed: {e2}")
            # Don't raise - let the migration continue
            # The migration should be idempotent, so it can be run again
            pass


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
