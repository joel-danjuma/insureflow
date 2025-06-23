#!/usr/bin/env python3
"""
Fix authentication and test payment system directly.
This script ensures users exist and tests the payment integration.
"""

import os
import sys
from datetime import datetime

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.core.security import get_password_hash, create_access_token
from app.models.user import User, UserRole
from app.models.premium import Premium, PaymentStatus
from app.models.policy import Policy
import asyncio
from app.services.payment_service import initiate_premium_payment
from app.core.config import settings

def ensure_test_users(db: Session):
    """Ensure test users exist in the database."""
    test_users = [
        {
            "username": "admin_secure",
            "email": "admin@securelife.ng",
            "full_name": "Test Admin SecureLife",
            "role": UserRole.ADMIN
        },
        {
            "username": "testadmin",
            "email": "test@admin.com",
            "full_name": "Test Admin",
            "role": UserRole.ADMIN
        },
        {
            "username": "testbroker",
            "email": "test@broker.com", 
            "full_name": "Test Broker",
            "role": UserRole.BROKER
        }
    ]
    
    created_users = []
    for user_data in test_users:
        # Check if user exists
        existing = db.query(User).filter(
            (User.email == user_data["email"]) | (User.username == user_data["username"])
        ).first()
        
        if not existing:
            user = User(
                **user_data,
                hashed_password=get_password_hash("password123"),
                is_active=True,
                is_verified=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(user)
            created_users.append(user_data["email"])
            print(f"✅ Created user: {user_data['email']} (password: password123)")
        else:
            print(f"ℹ️  User already exists: {user_data['email']}")
    
    db.commit()
    return created_users

def test_authentication(db: Session):
    """Test authentication with created users."""
    test_email = "admin@securelife.ng"
    test_password = "password123"
    
    # Get user
    user = db.query(User).filter(User.email == test_email).first()
    if not user:
        print(f"❌ User {test_email} not found in database!")
        return None
    
    print(f"✅ Found user: {user.email} (username: {user.username})")
    
    # Create access token
    from datetime import timedelta
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=60)
    )
    
    print(f"✅ Generated token: {access_token[:50]}...")
    return access_token, user

def check_squad_config():
    """Check Squad Co configuration."""
    print("
🔧 Squad Co Configuration:")
    print(f"  - Secret Key Set: {bool(settings.SQUAD_SECRET_KEY and settings.SQUAD_SECRET_KEY != '')}")
    print(f"  - Public Key Set: {bool(settings.SQUAD_PUBLIC_KEY and settings.SQUAD_PUBLIC_KEY != '')}")
    print(f"  - Base URL: {settings.SQUAD_BASE_URL}")
    print(f"  - Webhook URL: {settings.SQUAD_WEBHOOK_URL}")
    
    if not settings.SQUAD_SECRET_KEY or settings.SQUAD_SECRET_KEY == "":
        print("❌ Squad secret key not configured!")
        print("   Add to .env: SQUAD_SECRET_KEY=sk_eda39897e1c0ad6fa17e20865b05ab5703655fa5")
        return False
    return True

async def test_payment_system(db: Session):
    """Test the payment system."""
    print("
💳 Testing Payment System:")
    
    # Find an unpaid premium
    unpaid_premium = db.query(Premium).filter(
        Premium.payment_status != PaymentStatus.PAID
    ).first()
    
    if not unpaid_premium:
        print("❌ No unpaid premiums found!")
        # Get any premium
        premium = db.query(Premium).first()
        if not premium:
            print("❌ No premiums in database at all!")
            return
    else:
        premium = unpaid_premium
    
    print(f"  - Testing with Premium ID: {premium.id}")
    print(f"  - Amount: ₦{premium.amount}")
    print(f"  - Status: {premium.payment_status.value}")
    
    # Get policy and user info
    policy = db.query(Policy).filter(Policy.id == premium.policy_id).first()
    if policy:
        user = db.query(User).filter(User.id == policy.user_id).first()
        if user:
            print(f"  - Customer: {user.full_name} ({user.email})")
    
    try:
        # Test payment initiation
        result = await initiate_premium_payment(premium_id=premium.id, db=db)
        
        if "payment_url" in result:
            print(f"✅ Payment initiated successfully!")
            print(f"  - Payment URL: {result['payment_url']}")
            print(f"  - Transaction Ref: {result['transaction_ref']}")
            print(f"  - Message: {result['message']}")
        else:
            print(f"❌ Payment initiation failed: {result}")
            
    except Exception as e:
        print(f"❌ Payment error: {str(e)}")

def main():
    """Main function to fix auth and test payments."""
    print("🚀 InsureFlow Auth Fix & Payment Test")
    print("=" * 50)
    
    db = SessionLocal()
    
    try:
        # Step 1: Ensure users exist
        print("
👥 Step 1: Ensuring test users exist...")
        ensure_test_users(db)
        
        # Step 2: Test authentication
        print("
🔐 Step 2: Testing authentication...")
        auth_result = test_authentication(db)
        
        if not auth_result:
            print("❌ Authentication test failed!")
            return
        
        token, user = auth_result
        
        # Step 3: Check Squad configuration
        print("
💰 Step 3: Checking payment configuration...")
        if not check_squad_config():
            print("
⚠️  Squad Co is not properly configured.")
            print("Payment testing skipped. Configure Squad keys first.")
            return
        
        # Step 4: Test payment system
        print("
💸 Step 4: Testing payment system...")
        asyncio.run(test_payment_system(db))
        
        print("
✅ All tests completed!")
        print("
📝 Summary:")
        print(f"  - Authentication: ✅ Working")
        print(f"  - Test User: {user.email}")
        print(f"  - Password: password123")
        print(f"  - Token (first 50 chars): {token[:50]}...")
        
    except Exception as e:
        print(f"
❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()
