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
from app.models.premium import Premium
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
    Bypasses complex grouping to ensure data visibility for demo.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Fetch latest 50 successful payments directly
    payments = db.query(Payment).options(
        joinedload(Payment.premium).joinedload(Premium.policy).joinedload(Policy.broker),
        joinedload(Payment.premium).joinedload(Premium.policy).joinedload(Policy.user)
    ).filter(
        Payment.status == PaymentTransactionStatus.SUCCESS
    ).order_by(
        Payment.payment_date.desc()
    ).limit(limit).all()
    
    logger.debug(f"Found {len(payments)} successful payments for insurance firm dashboard")
    
    result = []
    
    for payment in payments:
        # Safety checks with defaults
        premium = payment.premium
        policy = premium.policy if premium else None
        
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
                # If no broker, maybe it's a direct user, verify if user is broker
                pass
                
            if policy.user:
                customer_name = policy.user.full_name

        # Map directly to frontend structure (LatestPayment type)
        # We treat every single payment as a "Latest Payment" row
        # This avoids complex grouping logic that might hide data
        result.append({
            "id": payment.transaction_reference or str(payment.id),
            "brokerName": broker_name,
            "totalAmount": float(payment.amount_paid),
            "policyCount": 1,  # 1 payment = 1 policy paid
            "paymentMethod": payment.payment_method.value if hasattr(payment.payment_method, 'value') else str(payment.payment_method),
            "status": "Successful", # Force friendly string
            "completedAt": payment.payment_date.isoformat(),
            "policies": [{
                "policyId": policy_id,
                "policyNumber": policy_number,
                "customerName": customer_name,
                "amount": float(payment.amount_paid)
            }]
        })
        
    return result
