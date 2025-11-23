import os
import sys
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the project root to the python path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.models.premium import Premium, PaymentStatus
from app.models.payment import Payment, PaymentTransactionStatus, PaymentMethod
from app.models.policy import Policy

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://insureflow:password@localhost:5432/insureflow")

def get_db_session():
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

def backfill_payments():
    db = get_db_session()
    try:
        print("🚀 Starting payment backfill process...")
        
        # 1. Find all PAID premiums
        paid_premiums = db.query(Premium).filter(
            Premium.payment_status == PaymentStatus.PAID
        ).all()
        
        print(f"✅ Found {len(paid_premiums)} premiums marked as PAID.")
        
        created_count = 0
        skipped_count = 0
        
        for premium in paid_premiums:
            # 2. Check if payment record exists
            existing_payment = db.query(Payment).filter(
                Payment.premium_id == premium.id,
                Payment.status == PaymentTransactionStatus.SUCCESS
            ).first()
            
            if existing_payment:
                # print(f"ℹ️ Payment already exists for Premium {premium.id}. Skipping.")
                skipped_count += 1
                continue
                
            # 3. Create missing payment record
            # Use premium amount if paid_amount is 0 or None (legacy data fix)
            amount = premium.paid_amount if premium.paid_amount and premium.paid_amount > 0 else premium.amount
            
            # Use payment_date if available, otherwise due_date, otherwise now
            payment_date = premium.payment_date if premium.payment_date else (premium.due_date if premium.due_date else datetime.utcnow())
            
            # Ensure payment_date is datetime (might be date object)
            if hasattr(payment_date, 'combine'):
                 payment_date = datetime.combine(payment_date, datetime.min.time())
            
            # Fetch policy for user details
            policy = db.query(Policy).filter(Policy.id == premium.policy_id).first()
            user_email = policy.user.email if policy and policy.user else "unknown@example.com"
            user_name = policy.user.full_name if policy and policy.user else "Unknown User"
            
            new_payment = Payment(
                premium_id=premium.id,
                amount_paid=amount,
                currency="NGN",
                payment_method=PaymentMethod.BANK_TRANSFER,
                status=PaymentTransactionStatus.SUCCESS,
                transaction_reference=f"BACKFILL-PREM-{premium.id}-{int(datetime.utcnow().timestamp())}",
                payment_date=payment_date,
                payer_email=user_email,
                payer_name=user_name,
                created_at=payment_date,
                updated_at=datetime.utcnow()
            )
            
            db.add(new_payment)
            created_count += 1
            
            if created_count % 50 == 0:
                print(f"   ...processed {created_count} records...")
                db.commit()
        
        db.commit()
        print(f"\n🎉 Backfill complete!")
        print(f"   - Created: {created_count} payment records")
        print(f"   - Skipped: {skipped_count} existing records")
        print(f"   - Total: {len(paid_premiums)} paid premiums processed")
        
    except Exception as e:
        print(f"❌ Error during backfill: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    backfill_payments()

