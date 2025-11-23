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
    import sys
    
    # Force logging to be visible
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    logger = logging.getLogger(__name__)
    
    result = []
    
    try:
        # 1. Fetch Premiums
        premiums = db.query(Premium).options(
            joinedload(Premium.policy).joinedload(Policy.broker),
            joinedload(Premium.policy).joinedload(Policy.user)
        ).filter(
            Premium.payment_status == PaymentStatus.PAID
        ).order_by(
            Premium.payment_date.desc()
        ).limit(limit).all()
        
        logger.info(f"✅ DASHBOARD: Found {len(premiums)} paid premiums")
        
        for premium in premiums:
            try:
                # Initialize safe defaults
                broker_name = "Direct/Unknown"
                customer_name = "Unknown Customer"
                policy_number = "N/A"
                policy_id = 0
                
                # Safely extract related data
                if premium.policy:
                    policy_id = premium.policy.id or 0
                    policy_number = premium.policy.policy_number or "N/A"
                    
                    if premium.policy.broker and premium.policy.broker.name:
                        broker_name = premium.policy.broker.name
                    
                    if premium.policy.user and premium.policy.user.full_name:
                        customer_name = premium.policy.user.full_name

                # Safely format date
                payment_date_str = datetime.utcnow().isoformat()
                if premium.payment_date:
                    if hasattr(premium.payment_date, 'isoformat'):
                        payment_date_str = premium.payment_date.isoformat()
                    else:
                        payment_date_str = str(premium.payment_date)

                # Safely get amount
                amount = float(premium.amount) if premium.amount else 0.0

                # Construct the result object
                result.append({
                    "id": str(premium.payment_reference or f"PAY-{premium.id}"),
                    "brokerName": broker_name,
                    "totalAmount": amount,
                    "policyCount": 1,
                    "paymentMethod": "Bank Transfer",
                    "status": "Success",
                    "completedAt": payment_date_str,
                    "policies": [{
                        "policyId": policy_id,
                        "policyNumber": policy_number,
                        "customerName": customer_name,
                        "amount": amount
                    }]
                })
            except Exception as inner_e:
                # If processing fails, return a minimal record instead of skipping!
                logger.error(f"⚠️ Recovering premium {premium.id}: {inner_e}")
                result.append({
                    "id": f"PAY-{premium.id}",
                    "brokerName": "Data Error",
                    "totalAmount": float(premium.amount or 0),
                    "policyCount": 1,
                    "paymentMethod": "Unknown",
                    "status": "Recovered",
                    "completedAt": datetime.utcnow().isoformat(),
                    "policies": []
                })

    except Exception as e:
        logger.error(f"❌ Critical DB Error: {e}")
        return []

    return result
