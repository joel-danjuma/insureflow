"""
API endpoints for payment-related operations.
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session
from typing import List
import json

from app.core.database import get_db
from app.schemas.payment import (
    PaymentInitiationResponse,
    PaymentInitiationRequest,
    BulkPaymentInitiationRequest,
)
from app.services import payment_service
from app.services.squad_co import squad_co_service
from app.crud import payment as crud_payment
from app.crud import premium as crud_premium
from app.crud import user as crud_user
from app.crud import policy as crud_policy

router = APIRouter()

@router.post("/webhook", status_code=status.HTTP_200_OK)
async def handle_squad_co_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Handles incoming webhooks from Squad Co.
    """
    squad_signature = request.headers.get("x-squad-signature")
    request_body = await request.body()
    
    # Verify the webhook signature
    if not squad_co_service.verify_webhook_signature(request_body, squad_signature):
        raise HTTPException(status_code=400, detail="Invalid webhook signature")
    
    try:
        # Parse the webhook payload
        payload = json.loads(request_body.decode('utf-8'))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid webhook payload: {e}")

    # Handle successful charge events
    event = payload.get("Event")
    if event == "charge.success":
        webhook_data = payload.get("Body", {})
        transaction_ref = webhook_data.get("transaction_ref")

        if not transaction_ref:
            raise HTTPException(status_code=400, detail="No transaction reference in webhook")

        # Check if this is a bulk payment
        metadata = webhook_data.get("meta_data", {})
        if metadata.get("type") == "bulk_payment" and "premium_ids" in metadata:
            premium_ids = metadata["premium_ids"]
            for premium_id in premium_ids:
                # Update premium status to paid
                crud_premium.update_premium_status_to_paid(db, premium_id=premium_id)
        else:
            # Handle single payment - find the premium by transaction ref
            payment = crud_payment.get_payment_by_transaction_ref(db, transaction_ref=transaction_ref)
            if payment and payment.premium_id:
                crud_premium.update_premium_status_to_paid(db, premium_id=payment.premium_id)

    # Acknowledge receipt of the webhook
    return {"status": "success"}

@router.post("/bulk-initiate", response_model=PaymentInitiationResponse)
async def initiate_bulk_policy_payment(
    request: BulkPaymentInitiationRequest,
    db: Session = Depends(get_db)
):
    """
    Initiates a bulk payment for multiple policies.
    """
    return await payment_service.initiate_bulk_policy_payment(
        policy_ids=request.policy_ids, db=db
    )

@router.post("/initiate/{premium_id}", response_model=PaymentInitiationResponse)
async def initiate_payment(
    premium_id: int,
    db: Session = Depends(get_db)
):
    """
    Initiates a payment for a premium.
    This endpoint is deprecated in favor of POST /premiums/{premium_id}/pay
    """
    return await payment_service.initiate_premium_payment(premium_id=premium_id, db=db)

@router.post("/initiate")
def initiate_payment(
    *,
    db: Session = Depends(get_db),
    payment_in: PaymentInitiationRequest,
):
    """
    Initiate a payment for a single policy.
    """
    return crud_payment.initiate(db=db, payment_in=payment_in)

@router.post("/bulk-initiate")
def initiate_bulk_payment(
    *,
    db: Session = Depends(get_db),
    bulk_payment_in: BulkPaymentInitiationRequest,
):
    """
    Initiate payment for multiple policies.
    """
    # This will be implemented in the crud layer
    return crud_payment.initiate_bulk(db=db, policy_ids=bulk_payment_in.policy_ids)

@router.get("/verify/{transaction_ref}")
async def verify_payment(
    transaction_ref: str,
    db: Session = Depends(get_db)
):
    """
    Verify a payment transaction with Squad Co.
    """
    # In a real implementation, you would call Squad's verify endpoint
    # For now, check our database
    payment = crud_payment.get_payment_by_transaction_ref(db, transaction_ref=transaction_ref)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    return {
        "transaction_ref": transaction_ref,
        "status": "success" if payment.premium_id else "pending",
        "amount": float(payment.amount_paid) if payment.amount_paid else 0,
        "premium_id": payment.premium_id
    }