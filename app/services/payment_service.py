"""
Service layer for payment-related operations.
"""
import uuid
import logging
from decimal import Decimal
from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.crud import premium as crud_premium
from app.crud import policy as crud_policy
from app.crud import user as crud_user
from app.crud import payment as crud_payment
from app.schemas.payment import PaymentCreate
from app.models.payment import PaymentMethod
from app.services.squad_co import squad_co_service
from app.services.virtual_account_service import virtual_account_service

# Add comprehensive logging
logger = logging.getLogger(__name__)

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
        amount=float(premium.amount),  # Pass amount in Naira as-is (no kobo conversion)
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
    Initiates bulk payment for multiple policies with comprehensive logging.
    """
    logger.info("🚀 INITIATING BULK POLICY PAYMENT")
    logger.info(f"📋 Policy IDs: {policy_ids}")
    
    if not policy_ids:
        logger.error("❌ No policy IDs provided")
        raise HTTPException(status_code=400, detail="No policy IDs provided.")

    try:
        # 1. Fetch all policies and validate
        logger.info("📊 FETCHING AND VALIDATING POLICIES")
        policies = []
        total_amount = Decimal('0')
        
        for policy_id in policy_ids:
            policy = crud_policy.get_policy(db, policy_id=policy_id)
            if not policy:
                logger.error(f"❌ Policy {policy_id} not found")
                raise HTTPException(status_code=404, detail=f"Policy {policy_id} not found")
            
            policies.append(policy)
            total_amount += policy.premium_amount
            logger.info(f"✅ Policy {policy_id}: {policy.policy_name} - ₦{policy.premium_amount:,.2f}")
        
        logger.info(f"💰 TOTAL BULK PAYMENT AMOUNT: ₦{total_amount:,.2f}")
        
        # 2. Get customer information
        customer = crud_user.get_user_by_id(db, user_id=policies[0].user_id)
        if not customer:
            logger.error(f"❌ Customer not found for user_id: {policies[0].user_id}")
            raise HTTPException(status_code=404, detail="Customer not found")
        
        logger.info(f"👤 Customer: {customer.full_name} ({customer.email})")
        
        # 3. Create virtual account for customer if not exists
        logger.info("🏦 CHECKING/CREATING CUSTOMER VIRTUAL ACCOUNT")
        virtual_account_result = await virtual_account_service.create_individual_virtual_account(
            db=db, user=customer
        )
        
        if virtual_account_result.get("success"):
            va = virtual_account_result.get("virtual_account")
            logger.info(f"✅ Customer Virtual Account: {va.get('account_number')} - {va.get('account_name')}")
            logger.info(f"🏦 Bank: {va.get('bank_name')}")
        else:
            logger.error(f"❌ Failed to create customer virtual account: {virtual_account_result.get('error')}")
            raise HTTPException(status_code=400, detail="Failed to create customer virtual account")
        
        # 4. Get unpaid premiums
        logger.info("📋 FETCHING UNPAID PREMIUMS")
        unpaid_premiums = crud_premium.get_unpaid_premiums_for_policies(db, policy_ids=policy_ids)
        
        if not unpaid_premiums:
            logger.warning("⚠️ No outstanding premiums found for the selected policies")
            raise HTTPException(status_code=400, detail="No outstanding premiums found for the selected policies.")
        
        unpaid_premium_ids = [p.id for p in unpaid_premiums]
        logger.info(f"📊 Found {len(unpaid_premiums)} unpaid premiums: {unpaid_premium_ids}")
        
        # 5. Initiate payment with Squad Co
        logger.info("💳 INITIATING SQUAD CO PAYMENT")
        logger.info(f"📊 Payment Details:")
        logger.info(f"   - Amount: ₦{total_amount:,.2f}")
        logger.info(f"   - Customer: {customer.email}")
        logger.info(f"   - Policies: {len(policies)}")
        logger.info(f"   - Premiums: {len(unpaid_premiums)}")
        
        payment_data = await squad_co_service.initiate_payment(
            amount=float(total_amount),
            email=customer.email,
            currency="NGN",
            metadata={
                "type": "bulk_payment",
                "policy_ids": policy_ids,
                "premium_ids": unpaid_premium_ids,
                "customer_va": va.get('account_number'),
                "total_amount": str(total_amount)
            }
        )
        
        if "error" in payment_data:
            logger.error(f"❌ Squad Co payment initiation failed: {payment_data['error']}")
            raise HTTPException(status_code=400, detail=payment_data["error"])
        
        if payment_data.get("status") != 200:
            logger.error(f"❌ Squad Co returned status {payment_data.get('status')}: {payment_data.get('message')}")
            raise HTTPException(status_code=400, detail=payment_data.get("message", "Payment initiation failed"))
        
        logger.info("✅ SQUAD CO PAYMENT INITIATED SUCCESSFULLY")
        logger.info(f"🔗 Payment URL: {payment_data.get('data', {}).get('checkout_url')}")
        logger.info(f"📝 Transaction Ref: {payment_data.get('data', {}).get('transaction_ref')}")
        
        # 6. Create payment records
        logger.info("💾 CREATING PAYMENT RECORDS")
        for premium in unpaid_premiums:
            payment = crud_payment.create_payment(
                db=db,
                payment=PaymentCreate(
                    premium_id=premium.id,
                    amount=premium.amount,
                    payment_method=PaymentMethod.BANK_TRANSFER,
                    transaction_reference=payment_data.get("data", {}).get("transaction_ref"),
                    status="pending"
                )
            )
            logger.info(f"✅ Payment record created for Premium {premium.id}: ₦{premium.amount:,.2f}")
        
        logger.info("🎉 BULK PAYMENT INITIATION COMPLETED SUCCESSFULLY")
        
        return {
            "success": True,
            "checkout_url": payment_data.get("data", {}).get("checkout_url"),
            "transaction_ref": payment_data.get("data", {}).get("transaction_ref"),
            "amount": float(total_amount),
            "customer_va": va.get('account_number'),
            "policies_count": len(policies),
            "premiums_count": len(unpaid_premiums),
            "message": "Bulk payment initiated successfully. Redirect to Squad Co for payment."
        }
        
    except Exception as e:
        logger.error(f"❌ BULK PAYMENT FAILED: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Bulk payment failed: {str(e)}") 