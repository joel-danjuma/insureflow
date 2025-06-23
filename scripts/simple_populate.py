#!/usr/bin/env python3
"""
Simple database population script for InsureFlow.
Creates basic test data for payments testing.
"""

import os
import sys
from datetime import datetime, date, timedelta
from decimal import Decimal
import random

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.company import InsuranceCompany
from app.models.broker import Broker
from app.models.policy import Policy, PolicyType, PolicyStatus
from app.models.premium import Premium, PaymentStatus, BillingCycle

def create_test_data(db: Session):
    """Create minimal test data for payment testing."""
    
    print("Creating insurance company...")
    # Create a test insurance company
    company = db.query(InsuranceCompany).filter(InsuranceCompany.name == "Test Insurance Co").first()
    if not company:
        company = InsuranceCompany(
            name="Test Insurance Co",
            registration_number="RC12345",
            contact_email="info@testinsurance.com",
            contact_phone="+234-1-234-5678",
            address="123 Test Street, Lagos",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(company)
        db.commit()
        print(f"✅ Created company: {company.name}")
    else:
        print(f"ℹ️  Company already exists: {company.name}")

    print("\nCreating customer...")
    # Create a test customer
    customer = db.query(User).filter(User.email == "customer@test.com").first()
    if not customer:
        customer = User(
            username="testcustomer",
            email="customer@test.com",
            full_name="Test Customer",
            role=UserRole.CUSTOMER,
            hashed_password=get_password_hash("password123"),
            is_active=True,
            is_verified=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(customer)
        db.commit()
        print(f"✅ Created customer: {customer.email}")
    else:
        print(f"ℹ️  Customer already exists: {customer.email}")

    print("\nCreating broker...")
    # Get or create a broker user
    broker_user = db.query(User).filter(User.email == "broker@test.com").first()
    if not broker_user:
        broker_user = User(
            username="testbroker",
            email="broker@test.com",
            full_name="Test Broker",
            role=UserRole.BROKER,
            hashed_password=get_password_hash("password123"),
            is_active=True,
            is_verified=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(broker_user)
        db.commit()
        print(f"✅ Created broker user: {broker_user.email}")
    
    # Create broker profile
    broker = db.query(Broker).filter(Broker.user_id == broker_user.id).first()
    if not broker:
        broker = Broker(
            user_id=broker_user.id,
            name="Test Broker",
            license_number="BRK-TEST-001",
            agency_name="Test Broker Agency",
            contact_email="broker@test.com",
            contact_phone="+234-800-000-0000",
            company_id=company.id,
            is_verified=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(broker)
        db.commit()
        print(f"✅ Created broker profile: {broker.name}")

    print("\nCreating policies...")
    # Create a few test policies
    policy_types = [PolicyType.LIFE, PolicyType.HEALTH, PolicyType.AUTO]
    policies = []
    
    for i, policy_type in enumerate(policy_types):
        policy_number = f"POL-TEST-{i+1:04d}"
        existing_policy = db.query(Policy).filter(Policy.policy_number == policy_number).first()
        
        if not existing_policy:
            policy = Policy(
                policy_number=policy_number,
                policy_type=policy_type,
                user_id=customer.id,
                company_id=company.id,
                broker_id=broker.id,
                status=PolicyStatus.ACTIVE,
                start_date=date.today() - timedelta(days=30),
                end_date=date.today() + timedelta(days=335),
                coverage_amount=str(1000000 * (i + 1)),  # 1M, 2M, 3M
                coverage_details=f'{{"type": "{policy_type.value}", "coverage": {1000000 * (i + 1)}}}',
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(policy)
            policies.append(policy)
            print(f"✅ Created policy: {policy.policy_number} ({policy_type.value})")
        else:
            policies.append(existing_policy)
            print(f"ℹ️  Policy already exists: {policy_number}")
    
    db.commit()

    print("\nCreating premiums...")
    # Create premiums for each policy
    premium_count = 0
    for policy in policies:
        # Create 3 premiums for each policy
        for month in range(3):
            premium_ref = f"PREM-{policy.policy_number}-{month+1:02d}"
            
            existing_premium = db.query(Premium).filter(
                Premium.premium_reference == premium_ref
            ).first()
            
            if not existing_premium:
                # First premium is paid, second is overdue, third is pending
                if month == 0:
                    payment_status = PaymentStatus.PAID
                    due_date = date.today() - timedelta(days=60)
                elif month == 1:
                    payment_status = PaymentStatus.OVERDUE
                    due_date = date.today() - timedelta(days=10)
                else:
                    payment_status = PaymentStatus.PENDING
                    due_date = date.today() + timedelta(days=20)
                
                premium = Premium(
                    policy_id=policy.id,
                    amount=Decimal("50000"),  # 50,000 Naira
                    currency="NGN",
                    due_date=due_date,
                    billing_cycle=BillingCycle.MONTHLY,
                    payment_status=payment_status,
                    premium_reference=premium_ref,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                
                if payment_status == PaymentStatus.PAID:
                    premium.paid_amount = premium.amount
                    premium.payment_date = due_date + timedelta(days=5)
                    premium.payment_reference = f"PAY-{premium_ref}"
                
                db.add(premium)
                premium_count += 1
                print(f"✅ Created premium: {premium_ref} ({payment_status.value})")
    
    db.commit()
    print(f"\n✅ Total premiums created: {premium_count}")

def main():
    """Main function."""
    print("🚀 Starting simple database population...")
    print("=" * 50)
    
    db = SessionLocal()
    
    try:
        create_test_data(db)
        
        # Show summary
        print("\n📊 Database Summary:")
        print(f"  - Companies: {db.query(InsuranceCompany).count()}")
        print(f"  - Users: {db.query(User).count()}")
        print(f"  - Policies: {db.query(Policy).count()}")
        print(f"  - Premiums: {db.query(Premium).count()}")
        print(f"  - Unpaid Premiums: {db.query(Premium).filter(Premium.payment_status != PaymentStatus.PAID).count()}")
        
        print("\n✅ Database population completed!")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
