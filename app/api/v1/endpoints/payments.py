"""
API endpoints for payment-related operations.
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.payment import (
    PaymentInitiationRequest, 
    PaymentInitiationResponse,
    SquadCoWebhookPayload,
    PaymentCreate,
)
from app.services import payment_service
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
        payload = SquadCoWebhookPayload.parse_raw(request_body)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid webhook payload: {e}")

    # Handle successful charge events
    if payload.event == "charge.success":
        webhook_data = payload.data
        
        # 1. Find the corresponding payment in our database
        payment = crud_payment.get_payment_by_transaction_ref(
            db, transaction_ref=webhook_data.transaction_reference
        )
        if not payment:
            # If payment not found, we might want to log this or handle it
            # For now, we'll just ignore it
            return Response(status_code=status.HTTP_200_OK)
            
        # 2. Update the payment status
        crud_payment.update_payment_status(db, payment=payment, webhook_data=webhook_data)
        
        # 3. Update the premium status to 'paid'
        if payment.premium_id:
            crud_premium.update_premium_status_to_paid(db, premium_id=payment.premium_id)
            
    # Acknowledge receipt of the webhook
    return Response(status_code=status.HTTP_200_OK)

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