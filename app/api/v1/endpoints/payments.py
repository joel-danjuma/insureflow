"""
API endpoints for payment-related operations.
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session
from typing import List
import json

from app.core.database import get_db
from app.dependencies import get_current_broker_or_admin_user
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
from app.models.user import User

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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_broker_or_admin_user)
):
    """
    Initiates a bulk payment for multiple policies.
    Requires broker or admin authentication.
    """
    return await payment_service.initiate_bulk_policy_payment(
        policy_ids=request.policy_ids, db=db
    )

# Single payment endpoint removed - use POST /premiums/{premium_id}/pay instead
# Duplicate endpoints removed - use the authenticated versions above

@router.get("/verify/{transaction_ref}")
async def verify_payment(
    transaction_ref: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_broker_or_admin_user)
):
    """
    Verify a payment transaction with Squad Co.
    Requires broker or admin authentication.
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

@router.get("/test-config")
async def test_payment_config(
    current_user: User = Depends(get_current_broker_or_admin_user)
):
    """
    Test endpoint to verify Squad Co configuration.
    Requires authentication.
    """
    from app.core.config import settings
    from app.services.squad_co import squad_co_service
    
    return {
        "squad_configured": bool(settings.SQUAD_SECRET_KEY and settings.SQUAD_SECRET_KEY != ""),
        "squad_base_url": settings.SQUAD_BASE_URL,
        "webhook_url": settings.SQUAD_WEBHOOK_URL,
        "has_secret_key": bool(squad_co_service.secret_key),
        "environment": "sandbox" if "sandbox" in settings.SQUAD_BASE_URL else "production"
    }

@router.post("/test-payment")
async def test_payment_initiation(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_broker_or_admin_user)
):
    """
    Test payment initiation with a small amount.
    Requires authentication.
    """
    # Find any unpaid premium
    unpaid_premium = crud_premium.get_unpaid_premiums_for_policies(db, policy_ids=[1, 2, 3, 4, 5])
    
    if not unpaid_premium:
        # Get any premium for testing
        premium = crud_premium.get_premium(db, premium_id=1)
        if not premium:
            raise HTTPException(status_code=404, detail="No premiums found in database")
    else:
        premium = unpaid_premium[0]
    
    try:
        result = await payment_service.initiate_premium_payment(premium_id=premium.id, db=db)
        return {
            "success": True,
            "premium_id": premium.id,
            "amount": float(premium.amount),
            "payment_url": result.get("payment_url"),
            "transaction_ref": result.get("transaction_ref"),
            "message": "Payment initiated successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "premium_id": premium.id,
            "amount": float(premium.amount) if premium else 0,
            "message": "Payment initiation failed"
        }