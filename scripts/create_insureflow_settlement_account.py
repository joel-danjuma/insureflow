#!/usr/bin/env python3
"""
Script to create the InsureFlow settlement virtual account.
This account is used for commission transfers and settlements.
"""

import sys
import os
from datetime import datetime
from decimal import Decimal

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.virtual_account import VirtualAccount, VirtualAccountType, VirtualAccountStatus
from app.models.user import User, UserRole
from app.core.security import get_password_hash

def create_insureflow_settlement_account():
    """Create the InsureFlow settlement virtual account."""
    db: Session = SessionLocal()
    
    try:
        # Check if the account already exists
        existing_account = db.query(VirtualAccount).filter(
            VirtualAccount.virtual_account_number == "3353296921"
        ).first()
        
        if existing_account:
            print(f"✅ InsureFlow settlement account already exists: {existing_account.virtual_account_number}")
            return existing_account
        
        # Check if we have an admin user to link to
        admin_user = db.query(User).filter(User.role == UserRole.INSUREFLOW_ADMIN).first()
        
        if not admin_user:
            print("🔧 Creating InsureFlow admin user for settlement account...")
            # Create a system admin user for the settlement account
            admin_user = User(
                username="insureflow_system",
                email="system@insureflow.com",
                hashed_password=get_password_hash("system_password_change_me"),
                full_name="InsureFlow System Account",
                role=UserRole.INSUREFLOW_ADMIN,
                is_active=True,
                is_verified=True,
                can_create_policies=False,
                can_make_payments=False,
                organization_name="InsureFlow Ltd"
            )
            db.add(admin_user)
            db.flush()  # Get the user ID
            print(f"✅ Created system admin user: {admin_user.email}")
        
        # Create the InsureFlow settlement virtual account
        settlement_account = VirtualAccount(
            user_id=admin_user.id,
            customer_identifier="INSUREFLOW_SETTLEMENT",
            virtual_account_number="3353296921",
            bank_code="058",  # Squad's bank code
            account_type=VirtualAccountType.BUSINESS,
            status=VirtualAccountStatus.ACTIVE,
            business_name="InsureFlow Settlement Account",
            email="settlement@insureflow.com",
            mobile_number="+2348000000000",
            address="InsureFlow Head Office, Lagos, Nigeria",
            total_credits=Decimal('0.00'),
            total_debits=Decimal('0.00'),
            current_balance=Decimal('0.00'),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(settlement_account)
        db.commit()
        
        print(f"✅ Successfully created InsureFlow settlement account:")
        print(f"   Account Number: {settlement_account.virtual_account_number}")
        print(f"   Customer ID: {settlement_account.customer_identifier}")
        print(f"   Business Name: {settlement_account.business_name}")
        print(f"   Linked to User: {admin_user.email}")
        
        return settlement_account
        
    except Exception as e:
        print(f"❌ Error creating InsureFlow settlement account: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def verify_settlement_account():
    """Verify that the settlement account exists and is properly configured."""
    db: Session = SessionLocal()
    
    try:
        account = db.query(VirtualAccount).filter(
            VirtualAccount.virtual_account_number == "3353296921"
        ).first()
        
        if not account:
            print("❌ InsureFlow settlement account not found!")
            return False
        
        print(f"✅ InsureFlow settlement account verified:")
        print(f"   ID: {account.id}")
        print(f"   Account Number: {account.virtual_account_number}")
        print(f"   Status: {account.status.value}")
        print(f"   Business Name: {account.business_name}")
        print(f"   Current Balance: ₦{account.current_balance:,.2f}")
        print(f"   User ID: {account.user_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verifying settlement account: {e}")
        return False
    finally:
        db.close()

def main():
    """Main function to create and verify the InsureFlow settlement account."""
    print("🏦 Creating InsureFlow Settlement Virtual Account...")
    print("=" * 60)
    
    try:
        # Create the settlement account
        account = create_insureflow_settlement_account()
        
        print("\n🔍 Verifying account creation...")
        print("-" * 40)
        
        # Verify the account was created successfully
        if verify_settlement_account():
            print("\n✅ InsureFlow settlement account setup completed successfully!")
            print("\n📋 This account will be used for:")
            print("   - Commission transfers from customer virtual accounts")
            print("   - Platform fee collection (1% total: 0.75% InsureFlow + 0.25% Habari)")
            print("   - Settlement processing to insurance companies")
        else:
            print("\n❌ Account verification failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Failed to create InsureFlow settlement account: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
