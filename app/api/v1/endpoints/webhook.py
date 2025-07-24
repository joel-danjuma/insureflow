from fastapi import APIRouter, Request, Header, HTTPException, Depends
import hmac
import hashlib
import os
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import Policy, Payment
from app.crud.policy import update_policy_payment_status

router = APIRouter()

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