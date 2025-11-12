"""create separate enums for virtual account transactions

Revision ID: create_vat_enums
Revises: update_vat_schema
Create Date: 2025-11-12 22:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = 'create_vat_enums'
down_revision = 'update_vat_schema'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create separate enums for virtual_account_transactions and migrate columns"""
    conn = op.get_bind()
    
    # Create new enums specifically for virtual account transactions
    # Note: PostgreSQL doesn't allow ADD VALUE in transactions, but CREATE TYPE works
    
    # Create vat_transactiontype enum
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE vat_transactiontype AS ENUM ('credit', 'debit', 'commission', 'settlement', 'refund');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # Create vat_transactionstatus enum
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE vat_transactionstatus AS ENUM ('pending', 'completed', 'failed', 'reversed');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # Create vat_transactionindicator enum with 'C' and 'D' values
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE vat_transactionindicator AS ENUM ('C', 'D');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # Convert transaction_type column from transactiontype to vat_transactiontype
    # First convert to text, then to new enum
    op.execute("""
        ALTER TABLE virtual_account_transactions 
        ALTER COLUMN transaction_type TYPE text USING transaction_type::text;
    """)
    
    # Map any existing values and convert to new enum
    # Since old enum might have different values, we'll handle conversion
    op.execute("""
        ALTER TABLE virtual_account_transactions 
        ALTER COLUMN transaction_type TYPE vat_transactiontype 
        USING CASE 
            WHEN transaction_type IN ('credit', 'debit', 'commission', 'settlement', 'refund') 
            THEN transaction_type::vat_transactiontype
            ELSE 'credit'::vat_transactiontype  -- Default fallback
        END;
    """)
    
    # Convert status column from transactionstatus to vat_transactionstatus
    op.execute("""
        ALTER TABLE virtual_account_transactions 
        ALTER COLUMN status TYPE text USING status::text;
    """)
    
    op.execute("""
        ALTER TABLE virtual_account_transactions 
        ALTER COLUMN status TYPE vat_transactionstatus 
        USING CASE 
            WHEN status IN ('pending', 'completed', 'failed', 'reversed') 
            THEN status::vat_transactionstatus
            WHEN status = 'cancelled' THEN 'failed'::vat_transactionstatus  -- Map cancelled to failed
            ELSE 'pending'::vat_transactionstatus  -- Default fallback
        END;
    """)
    
    # Convert transaction_indicator column from transactionindicator to vat_transactionindicator
    # Old enum has 'credit', 'debit' but we need 'C', 'D'
    op.execute("""
        ALTER TABLE virtual_account_transactions 
        ALTER COLUMN transaction_indicator TYPE text USING transaction_indicator::text;
    """)
    
    op.execute("""
        ALTER TABLE virtual_account_transactions 
        ALTER COLUMN transaction_indicator TYPE vat_transactionindicator 
        USING CASE 
            WHEN transaction_indicator = 'C' THEN 'C'::vat_transactionindicator
            WHEN transaction_indicator = 'D' THEN 'D'::vat_transactionindicator
            WHEN transaction_indicator = 'credit' THEN 'C'::vat_transactionindicator
            WHEN transaction_indicator = 'debit' THEN 'D'::vat_transactionindicator
            ELSE 'C'::vat_transactionindicator  -- Default fallback
        END;
    """)


def downgrade() -> None:
    """Revert to using shared enums"""
    # Convert back to text first
    op.execute("""
        ALTER TABLE virtual_account_transactions 
        ALTER COLUMN transaction_type TYPE text USING transaction_type::text;
    """)
    
    op.execute("""
        ALTER TABLE virtual_account_transactions 
        ALTER COLUMN transaction_type TYPE transactiontype 
        USING transaction_type::transactiontype;
    """)
    
    op.execute("""
        ALTER TABLE virtual_account_transactions 
        ALTER COLUMN status TYPE text USING status::text;
    """)
    
    op.execute("""
        ALTER TABLE virtual_account_transactions 
        ALTER COLUMN status TYPE transactionstatus 
        USING status::transactionstatus;
    """)
    
    op.execute("""
        ALTER TABLE virtual_account_transactions 
        ALTER COLUMN transaction_indicator TYPE text USING transaction_indicator::text;
    """)
    
    # Convert 'C'/'D' back to 'credit'/'debit' for old enum
    op.execute("""
        ALTER TABLE virtual_account_transactions 
        ALTER COLUMN transaction_indicator TYPE transactionindicator 
        USING CASE 
            WHEN transaction_indicator = 'C' THEN 'credit'::transactionindicator
            WHEN transaction_indicator = 'D' THEN 'debit'::transactionindicator
            ELSE 'credit'::transactionindicator
        END;
    """)
    
    # Drop the new enum types
    op.execute("DROP TYPE IF EXISTS vat_transactionindicator")
    op.execute("DROP TYPE IF EXISTS vat_transactionstatus")
    op.execute("DROP TYPE IF EXISTS vat_transactiontype")

