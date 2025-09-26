from fastapi import APIRouter, Request, Header, HTTPException, Depends
import hmac
import hashlib
import os
import logging
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import Policy, Payment
from app.crud.policy import update_policy_payment_status
from app.services.virtual_account_service import virtual_account_service

router = APIRouter()
logger = logging.getLogger(__name__)

SQUAD_SECRET_KEY = os.getenv("SQUAD_SECRET_KEY")

@router.post("/webhook/squad")
async def squad_webhook(request: Request, x_squad_encrypted_body: str = Header(None), db: Session = Depends(get_db)):
    payload = await request.json()
    tx_ref = payload.get("transaction_reference")
    amount_received = payload.get("amount_received")
    merchant_ref = payload.get("merchant_reference")
    # Compute hash
    data = f"{tx_ref}{amount_received}{merchant_ref}"
    computed_hash = hmac.new(
        SQUAD_SECRET_KEY.encode(),
        data.encode(),
        hashlib.sha512
    ).hexdigest()
    if computed_hash != x_squad_encrypted_body:
        raise HTTPException(status_code=401, detail="Invalid signature")
    # Idempotency check (implement a check in your DB)
    if db.query(Payment).filter(Payment.transaction_reference == tx_ref).first():
        return {"status": "ok"}
    # Process payment status
    status = payload.get("transaction_status")
    if status == "SUCCESS":
        update_policy_payment_status(db, merchant_ref, "paid", tx_ref)
    elif status == "MISMATCH":
        update_policy_payment_status(db, merchant_ref, "mismatch", tx_ref)
    elif status == "EXPIRED":
        update_policy_payment_status(db, merchant_ref, "expired", tx_ref)
    # Log the webhook
    # ...
    return {"status": "ok"}

@router.post("/webhook/squad/virtual-account")
async def squad_virtual_account_webhook(
    request: Request, 
    x_squad_encrypted_body: str = Header(None), 
    db: Session = Depends(get_db)
):
    """
    Handle Squad virtual account payment webhooks.
    This endpoint processes payments made to policy-specific virtual accounts.
    """
    try:
        payload = await request.json()
        logger.info(f"Received Squad virtual account webhook: {payload}")
        
        # Verify webhook signature
        if x_squad_encrypted_body and SQUAD_SECRET_KEY:
            virtual_account_number = payload.get("virtual_account_number", "")
            transaction_amount = payload.get("transaction_amount", "")
            transaction_ref = payload.get("transaction_reference", "")
            
            # Create verification string
            verification_string = f"{virtual_account_number}{transaction_amount}{transaction_ref}"
            computed_hash = hmac.new(
                SQUAD_SECRET_KEY.encode(),
                verification_string.encode(),
                hashlib.sha512
            ).hexdigest()
            
            if computed_hash != x_squad_encrypted_body:
                logger.error("Invalid webhook signature")
                raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Process the virtual account transaction
        result = virtual_account_service.process_webhook_transaction(db, payload)
        
        if result.get("error"):
            logger.error(f"Failed to process virtual account webhook: {result['error']}")
            raise HTTPException(status_code=500, detail=result["error"])
        
        logger.info(f"Virtual account webhook processed successfully: {result}")
        return {"status": "ok", "transaction_processed": True}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing virtual account webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Webhook processing failed: {str(e)}")

@router.post("/webhook/gaps/settlement-status")
async def gaps_settlement_status_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Handle GAPS settlement status updates.
    This endpoint receives notifications about settlement completion.
    """
    try:
        payload = await request.json()
        logger.info(f"Received GAPS settlement status webhook: {payload}")
        
        # Process GAPS settlement status update
        settlement_ref = payload.get("settlement_reference")
        status = payload.get("status")
        
        if settlement_ref and status:
            # Update settlement status in database
            from app.models.virtual_account_transaction import VirtualAccountTransaction
            
            transactions = db.query(VirtualAccountTransaction).filter(
                VirtualAccountTransaction.settlement_reference == settlement_ref
            ).all()
            
            for transaction in transactions:
                if status == "SUCCESS":
                    transaction.settlement_status = 'completed'
                elif status == "FAILED":
                    transaction.settlement_status = 'failed'
                else:
                    transaction.settlement_status = 'processing'
                
                transaction.gaps_transaction_ref = payload.get("gaps_reference")
            
            db.commit()
            logger.info(f"Updated {len(transactions)} transactions with settlement status: {status}")
        
        return {"status": "ok", "settlement_updated": True}
        
    except Exception as e:
        logger.error(f"Error processing GAPS settlement webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Webhook processing failed: {str(e)}") 