"""
CRUD operations for the Payment model.
"""
import json
from sqlalchemy.orm import Session
from app.models.payment import Payment
from app.schemas.payment import SquadCoTransactionData, PaymentCreate

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