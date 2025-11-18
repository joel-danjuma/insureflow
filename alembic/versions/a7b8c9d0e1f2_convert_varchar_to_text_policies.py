"""convert_varchar_to_text_policies

Revision ID: a7b8c9d0e1f2
Revises: 5b548823ce3e
Create Date: 2025-11-18 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a7b8c9d0e1f2'
down_revision: Union[str, None] = '5b548823ce3e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Convert ALL VARCHAR columns to TEXT to avoid OID 1043 errors.
    TEXT type doesn't have length constraints and won't trigger type 1043 issues.
    Also converts coverage_amount from VARCHAR to NUMERIC(15,2) to match the model.
    """
    conn = op.get_bind()
    
    # ALL VARCHAR columns to convert to TEXT
    columns_to_convert = [
        'merchant_reference',
        'payment_status',
        'transaction_reference',
        'policy_name',
        'policy_number',
        'company_name',
        'contact_person',
        'contact_email',
        'contact_phone',
        'rc_number'
    ]
    
    try:
        # Convert all VARCHAR columns to TEXT
        for column_name in columns_to_convert:
            # Check if column exists and is VARCHAR
            result = conn.execute(sa.text("""
                SELECT data_type
                FROM information_schema.columns 
                WHERE table_name = 'policies'
                AND column_name = :col_name
                AND table_schema = 'public'
            """), {"col_name": column_name})
            
            row = result.fetchone()
            if row and row[0] == 'character varying':
                # Convert to TEXT
                conn.execute(sa.text(f"""
                    ALTER TABLE policies 
                    ALTER COLUMN {column_name} 
                    TYPE TEXT
                    USING {column_name}::TEXT
                """))
                print(f"Converted column '{column_name}' from VARCHAR to TEXT")
        
        # Convert coverage_amount from VARCHAR to NUMERIC(15,2) to match the model
        result = conn.execute(sa.text("""
            SELECT data_type
            FROM information_schema.columns 
            WHERE table_name = 'policies'
            AND column_name = 'coverage_amount'
            AND table_schema = 'public'
        """))
        
        row = result.fetchone()
        if row and row[0] == 'character varying':
            conn.execute(sa.text("""
                ALTER TABLE policies 
                ALTER COLUMN coverage_amount 
                TYPE NUMERIC(15, 2)
                USING coverage_amount::NUMERIC(15, 2)
            """))
            print("Converted column 'coverage_amount' from VARCHAR to NUMERIC(15,2)")
        
        conn.commit()
    except Exception as e:
        print(f"Error converting columns: {e}")
        conn.rollback()
        raise


def downgrade() -> None:
    """
    Revert TEXT columns back to VARCHAR and NUMERIC back to VARCHAR (not recommended).
    """
    conn = op.get_bind()
    
    # Revert all TEXT columns back to VARCHAR with original lengths
    op.alter_column('policies', 'merchant_reference',
                   type_=sa.String(100),
                   existing_type=sa.Text(),
                   existing_nullable=True)
    
    op.alter_column('policies', 'payment_status',
                   type_=sa.String(50),
                   existing_type=sa.Text(),
                   existing_nullable=True)
    
    op.alter_column('policies', 'transaction_reference',
                   type_=sa.String(100),
                   existing_type=sa.Text(),
                   existing_nullable=True)
    
    op.alter_column('policies', 'policy_name',
                   type_=sa.String(255),
                   existing_type=sa.Text(),
                   existing_nullable=False)
    
    op.alter_column('policies', 'policy_number',
                   type_=sa.String(100),
                   existing_type=sa.Text(),
                   existing_nullable=False)
    
    op.alter_column('policies', 'company_name',
                   type_=sa.String(255),
                   existing_type=sa.Text(),
                   existing_nullable=False)
    
    op.alter_column('policies', 'contact_person',
                   type_=sa.String(255),
                   existing_type=sa.Text(),
                   existing_nullable=False)
    
    op.alter_column('policies', 'contact_email',
                   type_=sa.String(255),
                   existing_type=sa.Text(),
                   existing_nullable=False)
    
    op.alter_column('policies', 'contact_phone',
                   type_=sa.String(50),
                   existing_type=sa.Text(),
                   existing_nullable=True)
    
    op.alter_column('policies', 'rc_number',
                   type_=sa.String(100),
                   existing_type=sa.Text(),
                   existing_nullable=True)
    
    # Revert coverage_amount from NUMERIC back to VARCHAR
    op.alter_column('policies', 'coverage_amount',
                   type_=sa.String(20),
                   existing_type=sa.Numeric(15, 2),
                   existing_nullable=True)

