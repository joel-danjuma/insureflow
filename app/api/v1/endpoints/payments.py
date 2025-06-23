"""
API endpoints for payment-related operations.
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.payment import (
    PaymentInitiationResponse,
    PaymentInitiationRequest,
    SquadCoWebhookPayload,
    PaymentCreate,
    BulkPaymentInitiationRequest,
)
from app.services import payment_service
from app.services import squad_co
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
    if not squad_co.verify_webhook_signature(request_body, squad_signature):
        raise HTTPException(status_code=400, detail="Invalid webhook signature")
    
    try:
        payload = SquadCoWebhookPayload.parse_raw(request_body)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid webhook payload: {e}")

    # Handle successful charge events
    if payload.event == "charge.success":
        webhook_data = payload.data
        transaction_ref = webhook_data.transaction_reference

        # Check if this is a bulk payment
        metadata = webhook_data.get("metadata", {})
        if metadata.get("type") == "bulk_payment" and "premium_ids" in metadata:
            premium_ids = metadata["premium_ids"]
            for premium_id in premium_ids:
                payment = crud_payment.get_payment_by_premium_and_ref(db, premium_id=premium_id, transaction_ref=transaction_ref)
                if payment:
                    crud_payment.update_payment_status(db, payment=payment, webhook_data=webhook_data)
                    crud_premium.update_premium_status_to_paid(db, premium_id=premium_id)
        else:
            # Handle single payment
            payment = crud_payment.get_payment_by_transaction_ref(
                db, transaction_ref=transaction_ref
            )
            if payment:
                crud_payment.update_payment_status(db, payment=payment, webhook_data=webhook_data)
                if payment.premium_id:
                    crud_premium.update_premium_status_to_paid(db, premium_id=payment.premium_id)

    # Acknowledge receipt of the webhook
    return Response(status_code=status.HTTP_200_OK)

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
def verify_payment(
    *,
    transaction_ref: str,
    db: Session = Depends(get_db)
):
    # This method is not provided in the original file or the new code block
    # It's assumed to exist as it's called in the verify_payment method
    pass