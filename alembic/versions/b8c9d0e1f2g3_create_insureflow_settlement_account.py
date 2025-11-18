"""create_insureflow_settlement_account

Revision ID: b8c9d0e1f2g3
Revises: a7b8c9d0e1f2
Create Date: 2025-11-18 15:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision: str = 'b8c9d0e1f2g3'
down_revision: Union[str, None] = 'a7b8c9d0e1f2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Create the InsureFlow settlement virtual account and system admin user.
    This account is used for commission transfers and settlements.
    """
    conn = op.get_bind()
    
    try:
        # First, check if we need to create a system admin user
        result = conn.execute(sa.text("""
            SELECT id FROM users 
            WHERE email = 'system@insureflow.com' 
            OR role = 'INSUREFLOW_ADMIN'
            LIMIT 1
        """))
        
        admin_user_row = result.fetchone()
        
        if not admin_user_row:
            # Create system admin user for the settlement account
            conn.execute(sa.text("""
                INSERT INTO users (
                    username, email, hashed_password, full_name, role,
                    is_active, is_verified, can_create_policies, can_make_payments,
                    organization_name, created_at, updated_at
                ) VALUES (
                    'insureflow_system',
                    'system@insureflow.com',
                    '$2b$12$LQv3c1yqBw2LeOuN2PL2L.gtEHOOyy4XxukW8kQ8z9JfheoQfenmu', -- hashed 'system_password_change_me'
                    'InsureFlow System Account',
                    'INSUREFLOW_ADMIN',
                    true,
                    true,
                    false,
                    false,
                    'InsureFlow Ltd',
                    NOW(),
                    NOW()
                ) RETURNING id
            """))
            
            # Get the newly created user ID
            result = conn.execute(sa.text("""
                SELECT id FROM users WHERE email = 'system@insureflow.com'
            """))
            admin_user_row = result.fetchone()
            print("Created system admin user for InsureFlow settlement account")
        
        admin_user_id = admin_user_row[0]
        
        # Check if the settlement account already exists
        result = conn.execute(sa.text("""
            SELECT id FROM virtual_accounts 
            WHERE virtual_account_number = '3353296921'
        """))
        
        existing_account = result.fetchone()
        
        if not existing_account:
            # Create the InsureFlow settlement virtual account
            conn.execute(sa.text("""
                INSERT INTO virtual_accounts (
                    user_id, customer_identifier, virtual_account_number, bank_code,
                    account_type, status, business_name, email, mobile_number, address,
                    total_credits, total_debits, current_balance, created_at, updated_at
                ) VALUES (
                    :user_id,
                    'INSUREFLOW_SETTLEMENT',
                    '3353296921',
                    '058',
                    'BUSINESS',
                    'ACTIVE',
                    'InsureFlow Settlement Account',
                    'settlement@insureflow.com',
                    '+2348000000000',
                    'InsureFlow Head Office, Lagos, Nigeria',
                    0.00,
                    0.00,
                    0.00,
                    NOW(),
                    NOW()
                )
            """), {"user_id": admin_user_id})
            
            print("Created InsureFlow settlement virtual account: 3353296921")
        else:
            print("InsureFlow settlement account already exists")
        
        conn.commit()
        
    except Exception as e:
        print(f"Error creating InsureFlow settlement account: {e}")
        conn.rollback()
        raise


def downgrade() -> None:
    """
    Remove the InsureFlow settlement virtual account and system admin user.
    """
    conn = op.get_bind()
    
    try:
        # Remove the settlement virtual account
        conn.execute(sa.text("""
            DELETE FROM virtual_accounts 
            WHERE virtual_account_number = '3353296921'
        """))
        
        # Remove the system admin user (only if it was created by this migration)
        conn.execute(sa.text("""
            DELETE FROM users 
            WHERE email = 'system@insureflow.com' 
            AND username = 'insureflow_system'
        """))
        
        conn.commit()
        print("Removed InsureFlow settlement account and system admin user")
        
    except Exception as e:
        print(f"Error removing InsureFlow settlement account: {e}")
        conn.rollback()
        raise
