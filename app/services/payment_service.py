"""
Service layer for payment-related operations.
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.crud import premium as crud_premium
from app.crud import policy as crud_policy
from app.crud import user as crud_user
from app.crud import payment as crud_payment
from app.schemas.payment import PaymentCreate
from app.services.squad_co import squad_co_service

async def initiate_premium_payment(premium_id: int, db: Session):
    """
    Orchestrates the initiation of a payment for a premium.
    """
    # 1. Fetch the premium from the database
    premium = crud_premium.get_premium(db, premium_id=premium_id)
    if not premium:
        raise HTTPException(status_code=404, detail="Premium not found")
    if premium.status == 'paid':
        raise HTTPException(status_code=400, detail="Premium has already been paid")

    # 2. Fetch the policy and user to get the email
    policy = crud_policy.get_policy(db, policy_id=premium.policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found for this premium")
    
    customer = crud_user.get_user_by_id(db, user_id=policy.customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found for this policy")

    # 3. Initiate payment with Squad Co
    payment_data = await squad_co_service.initiate_payment(
        amount=int(premium.amount), # Ensure amount is integer (kobo/cents)
        email=customer.email,
        currency="NGN", # Or get from config/policy
        metadata={"premium_id": premium_id, "policy_id": policy.id}
    )

    if "error" in payment_data:
        raise HTTPException(status_code=400, detail=payment_data["error"])
        
    if payment_data.get("status") != 200:
        raise HTTPException(status_code=400, detail=payment_data.get("message", "Payment initiation failed."))

    data = payment_data.get("data", {})
    checkout_url = data.get("checkout_url")
    transaction_ref = data.get("transaction_reference")

    if not checkout_url or not transaction_ref:
        raise HTTPException(status_code=500, detail="Could not retrieve checkout URL or transaction reference from Squad Co.")

    # 4. Create a payment record in our database
    payment_create = PaymentCreate(
        premium_id=premium_id,
        amount_paid=premium.amount,
        payment_method="card", # Or determine from request/gateway
        transaction_reference=transaction_ref,
        payer_email=customer.email
    )
    crud_payment.create_payment(db=db, payment=payment_create)

    return {
        "payment_url": checkout_url,
        "transaction_ref": transaction_ref,
        "message": "Payment initiated successfully. Please proceed to the payment URL."
    } 