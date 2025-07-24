"""
Service layer for payment-related operations.
"""
import uuid
from decimal import Decimal
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.crud import premium as crud_premium
from app.crud import policy as crud_policy
from app.crud import user as crud_user
from app.crud import payment as crud_payment
from app.schemas.payment import PaymentCreate
from app.models.payment import PaymentMethod
from app.services.squad_co import squad_co_service

async def initiate_premium_payment(premium_id: int, db: Session):
    """
    Orchestrates the initiation of a payment for a premium.
    """
    # 1. Fetch the premium from the database
    premium = crud_premium.get_premium(db, premium_id=premium_id)
    if not premium:
        raise HTTPException(status_code=404, detail="Premium not found")
    if premium.payment_status.value == 'paid':
        raise HTTPException(status_code=400, detail="Premium has already been paid")

    # 2. Fetch the policy and user to get the email
    policy = crud_policy.get_policy(db, policy_id=premium.policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found for this premium")
    
    customer = crud_user.get_user_by_id(db, user_id=policy.user_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found for this policy")

    # 3. Initiate payment with Squad Co
    payment_data = await squad_co_service.initiate_payment(
        amount=float(premium.amount),  # Pass amount in Naira, squad service will convert to kobo
        email=customer.email,
        currency="NGN",
        metadata={"premium_id": premium_id, "policy_id": policy.id}
    )

    if "error" in payment_data:
        raise HTTPException(status_code=400, detail=payment_data["error"])
        
    if payment_data.get("status") != 200:
        raise HTTPException(status_code=400, detail=payment_data.get("message", "Payment initiation failed."))

    data = payment_data.get("data", {})
    checkout_url = data.get("checkout_url")
    transaction_ref = data.get("transaction_ref")  # Fixed: was transaction_reference

    if not checkout_url or not transaction_ref:
        raise HTTPException(status_code=500, detail="Could not retrieve checkout URL or transaction reference from Squad Co.")

    # 4. Create a payment record in our database
    payment_create = PaymentCreate(
        premium_id=premium_id,
        amount_paid=Decimal(str(premium.amount)),  # Convert to Decimal
        payment_method=PaymentMethod.CARD,  # Use proper enum
        transaction_reference=transaction_ref,
        payer_email=customer.email
    )
    crud_payment.create_payment(db=db, payment=payment_create)

    return {
        "payment_url": checkout_url,
        "transaction_ref": transaction_ref,
        "message": "Payment initiated successfully. Please proceed to the payment URL."
    }

async def initiate_bulk_premium_payment(premium_ids: list[int], db: Session):
    """
    Orchestrates the initiation of a bulk payment for multiple premiums.
    This is a simulated version that does not call the Squad API.
    """
    if not premium_ids:
        raise HTTPException(status_code=400, detail="No premium IDs provided.")

    premiums = crud_premium.get_premiums_by_ids(db, premium_ids=premium_ids)
    if len(premiums) != len(premium_ids):
        raise HTTPException(status_code=404, detail="One or more premiums not found.")

    total_amount = Decimal('0')
    customer_email = None
    policy_ids = set()

    for premium in premiums:
        if premium.payment_status.value == 'paid':
            raise HTTPException(status_code=400, detail=f"Premium {premium.id} has already been paid.")
        total_amount += premium.amount
        policy_ids.add(premium.policy_id)

    # Assume all premiums in a bulk payment belong to the same customer
    first_policy = crud_policy.get_policy(db, policy_id=list(policy_ids)[0])
    if not first_policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    customer = crud_user.get_user_by_id(db, user_id=first_policy.user_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found for this policy")
    customer_email = customer.email

    # Simulate a successful payment
    transaction_ref = f"simulated_bulk_{uuid.uuid4()}"

    for premium in premiums:
        # Create a payment record
        payment_create = PaymentCreate(
            premium_id=premium.id,
            amount_paid=premium.amount,
            payment_method=PaymentMethod.VIRTUAL_ACCOUNT,
            transaction_reference=transaction_ref,
            payer_email=customer_email
        )
        crud_payment.create_payment(db=db, payment=payment_create)

        # Update the premium status
        crud_premium.update_premium_status(db=db, premium_id=premium.id, status="paid")

    return {
        "payment_url": f"https://example.com/simulated-payment/{transaction_ref}",
        "transaction_ref": transaction_ref,
        "message": "Bulk payment successfully simulated."
    }

async def initiate_bulk_policy_payment(policy_ids: list[int], db: Session):
    """
    Finds all unpaid premiums for a list of policies and initiates a bulk payment.
    """
    if not policy_ids:
        raise HTTPException(status_code=400, detail="No policy IDs provided.")

    unpaid_premiums = crud_premium.get_unpaid_premiums_for_policies(db, policy_ids=policy_ids)
    
    if not unpaid_premiums:
        raise HTTPException(status_code=400, detail="No outstanding premiums found for the selected policies.")

    unpaid_premium_ids = [p.id for p in unpaid_premiums]

    return await initiate_bulk_premium_payment(premium_ids=unpaid_premium_ids, db=db) 