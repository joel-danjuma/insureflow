"""
CRUD operations for the Payment model.
"""
import json
from typing import List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from app.models.payment import Payment, PaymentTransactionStatus
from app.schemas.payment import SquadCoTransactionData, PaymentCreate
from app.models.premium import Premium, PaymentStatus
from app.models.policy import Policy
from app.models.broker import Broker
from app.models.user import User

def create_payment(db: Session, payment: PaymentCreate) -> Payment:
    """
    Creates a new payment record in the database.
    """
    db_payment = Payment(**payment.model_dump())
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment

def get_payment_by_transaction_ref(db: Session, transaction_ref: str) -> Payment | None:
    """
    Retrieves a payment from the database by its transaction reference.
    """
    return db.query(Payment).filter(Payment.transaction_reference == transaction_ref).first()

def get_payment_by_premium_and_ref(db: Session, premium_id: int, transaction_ref: str):
    """
    Retrieves a specific payment record for a premium using a transaction reference.
    """
    return db.query(Payment).filter(
        Payment.premium_id == premium_id,
        Payment.transaction_reference == transaction_ref
    ).first()

def update_payment_status(db: Session, payment: Payment, webhook_data: SquadCoTransactionData) -> Payment:
    """
    Updates the status of a payment based on webhook data.
    """
    payment.status = webhook_data.status
    payment.gateway_response = json.dumps(webhook_data.model_dump())
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment

def initiate_bulk(db: Session, policy_ids: list[int]):
    """
    Placeholder for initiating bulk payment for multiple policies.
    """
    # In a real implementation, this would iterate through policy_ids,
    # find associated unpaid premiums, and call the payment gateway.
    print(f"Initiating bulk payment for policy IDs: {policy_ids}")
    return {"status": "success", "message": "Bulk payment initiation started.", "policy_ids": policy_ids}

def get_payments_for_insurance_firm(db: Session, skip: int = 0, limit: int = 50) -> List[Dict[str, Any]]:
    """
    SIMPLIFIED: Get latest successful payments.
    Directly fetches PAID PREMIUMS to guarantee data visibility on dashboard.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # ✅ Add detailed logging to see what's happening
    total_paid_count = db.query(Premium).filter(
        Premium.payment_status == PaymentStatus.PAID
    ).count()
    
    logger.info(f"🔍 Total PAID premiums in database: {total_paid_count}")
    
    # Fetch PAID premiums directly to ensure we show what is in the DB
    # This bypasses potential issues with the 'payments' table sync
    premiums = db.query(Premium).options(
        joinedload(Premium.policy).joinedload(Policy.broker),
        joinedload(Premium.policy).joinedload(Policy.user)
    ).filter(
        Premium.payment_status == PaymentStatus.PAID
    ).order_by(
        Premium.payment_date.desc(),  # Prioritize payment_date
        Premium.updated_at.desc()     # Fallback to update time
    ).limit(limit).all()
    
    logger.info(f"✅ Found {len(premiums)} paid premiums for insurance firm dashboard (limit: {limit})")
    
    result = []
    
    for premium in premiums:
        try:
            # Safety checks with defaults
            policy = premium.policy
            
            # Fallback data if relationships are missing
            broker_name = "Direct Client"
            customer_name = "Unknown Customer"
            policy_number = "N/A"
            policy_id = 0
            
            if policy:
                policy_id = policy.id
                policy_number = policy.policy_number
                if policy.broker:
                    broker_name = policy.broker.name
                elif policy.user:
                    # If no broker, maybe it's a direct user
                    pass
                    
                if policy.user:
                    customer_name = policy.user.full_name
            else:
                logger.warning(f"⚠️ Premium {premium.id} has no associated policy")

            # Determine payment date
            payment_date = premium.payment_date or premium.updated_at or datetime.utcnow()
            if hasattr(payment_date, 'isoformat'):
                payment_date_str = payment_date.isoformat()
            else:
                payment_date_str = str(payment_date)

            # Map directly to frontend structure (LatestPayment type)
            result.append({
                "id": premium.payment_reference or f"PAY-{premium.id}",
                "brokerName": broker_name,
                "totalAmount": float(premium.amount), # Use full premium amount
                "policyCount": 1,
                "paymentMethod": "Bank Transfer", # Default
                "status": "Success",
                "completedAt": payment_date_str,
                "policies": [{
                    "policyId": policy_id,
                    "policyNumber": policy_number,
                    "customerName": customer_name,
                    "amount": float(premium.amount)
                }]
            })
        except Exception as e:
            logger.error(f"❌ Error processing premium {premium.id}: {str(e)}", exc_info=True)
            continue
        
    logger.info(f"📊 Returning {len(result)} payment records")
    return result
