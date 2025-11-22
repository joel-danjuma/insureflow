"""
Script to generate missing premiums for existing policies.
"""
import os
import sys
from datetime import datetime, timedelta
from decimal import Decimal

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, joinedload

from app.core.config import settings
from app.models.policy import Policy, PolicyStatus
from app.models.premium import Premium, PaymentStatus
from app.models.user import User

# Ensure settings are loaded
if not settings.DATABASE_URL:
    print("DATABASE_URL not set. Please ensure .env is configured.")
    sys.exit(1)

# Create engine and session
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def generate_missing_premiums():
    db = SessionLocal()
    try:
        print("🚀 Checking for policies without premiums...")
        
        # Get all active policies
        policies = db.query(Policy).filter(
            Policy.status == PolicyStatus.ACTIVE
        ).options(joinedload(Policy.user)).all()
        
        print(f"Found {len(policies)} active policies.")
        
        created_count = 0
        
        for policy in policies:
            # Check if policy already has premiums
            existing_premiums = db.query(Premium).filter(
                Premium.policy_id == policy.id
            ).count()
            
            if existing_premiums == 0:
                print(f"📝 Creating premium for Policy {policy.policy_number} ({policy.policy_name})")
                
                # Create a pending premium
                premium = Premium(
                    policy_id=policy.id,
                    amount=policy.premium_amount,
                    due_date=policy.next_payment_date or (datetime.now() + timedelta(days=30)).date(),
                    payment_status=PaymentStatus.PENDING,
                    payment_date=None,
                    transaction_reference=None
                )
                db.add(premium)
                created_count += 1
        
        db.commit()
        print(f"\n✅ Successfully created {created_count} missing premiums!")
        
    except Exception as e:
        print(f"❌ Error generating premiums: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    generate_missing_premiums()

