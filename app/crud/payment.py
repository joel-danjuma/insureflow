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
    Get payments grouped by broker and payment date for insurance firm dashboard.
    Returns formatted data matching LatestPayment type from frontend.
    """
    # Query successful payments with all necessary relationships
    payments = db.query(Payment).options(
        joinedload(Payment.premium).joinedload(Premium.policy).joinedload(Policy.broker),
        joinedload(Payment.premium).joinedload(Premium.policy).joinedload(Policy.user)
    ).filter(
        Payment.status == PaymentTransactionStatus.SUCCESS
    ).order_by(
        Payment.payment_date.desc()
    ).offset(skip).limit(limit * 10).all()  # Get more to group, then limit after grouping
    
    # Group payments by broker and payment date
    grouped_payments: Dict[str, Dict[str, Any]] = {}
    
    for payment in payments:
        premium = payment.premium
        if not premium:
            continue
            
        policy = premium.policy
        if not policy:
            continue
        
        broker_name = policy.broker.name if policy.broker else "Unassigned"
        broker_id = policy.broker.id if policy.broker else 0
        
        # Create a key for grouping: broker_id + date (without time)
        payment_date_key = payment.payment_date.date().isoformat()
        group_key = f"{broker_id}_{payment_date_key}"
        
        if group_key not in grouped_payments:
            grouped_payments[group_key] = {
                "id": payment.transaction_reference.split("_premium_")[0] if "_premium_" in payment.transaction_reference else payment.transaction_reference,
                "brokerId": broker_id,
                "brokerName": broker_name,
                "totalAmount": 0,
                "policyCount": 0,
                "paymentMethod": payment.payment_method.value,
                "status": payment.status.value,
                "completedAt": payment.payment_date.isoformat(),
                "policies": []
            }
        
        # Add to grouped payment
        grouped = grouped_payments[group_key]
        grouped["totalAmount"] += float(payment.amount_paid)
        
        # Add policy details if not already added
        policy_exists = any(p["policyId"] == policy.id for p in grouped["policies"])
        if not policy_exists:
            grouped["policies"].append({
                "policyId": policy.id,
                "policyNumber": policy.policy_number,
                "customerName": policy.user.full_name if policy.user else "Unknown",
                "amount": float(payment.amount_paid)
            })
            grouped["policyCount"] = len(grouped["policies"])
    
    # Convert to list and sort by completedAt descending
    result = list(grouped_payments.values())
    result.sort(key=lambda x: x["completedAt"], reverse=True)
    
    # Limit results
    return result[:limit] 