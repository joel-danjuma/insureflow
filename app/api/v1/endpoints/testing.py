"""
Testing API endpoints for payment flow simulation and stakeholder demonstrations.
Provides comprehensive logging and real-time feedback for dashboard testing.
"""
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from app.core.config import settings
from app.core.database import get_db
from app.dependencies import get_current_broker_or_admin_user
from app.models.user import User
from app.crud import user as crud_user, premium as crud_premium, virtual_account as crud_virtual_account, policy as crud_policy
from app.schemas.testing import (
    TestVAAccountCreationRequest, 
    TestVAFundingRequest, 
    TestVATransferRequest,
    SimulatePaymentRequest
)
from app.services.virtual_account_service import virtual_account_service
from app.services.squad_co import squad_co_service
from app.services.settlement_service import settlement_service

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/simulate-payment", response_model=dict, tags=["Testing"])
async def simulate_payment(
    request: SimulatePaymentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_broker_or_admin_user)
):
    """
    Simulates a full end-to-end payment and settlement flow for a given premium.
    1. Ensures a virtual account exists for the user.
    2. Simulates a payment TO the user's virtual account.
    3. Simulates the webhook processing by updating balances and policy status.
    4. Triggers the settlement FROM the user's virtual account to the insurance firm.
    """
    logger.info(f"--- 🧪 Test: Simulating full payment flow for Premium ID: {request.premium_id} ---")

    premium = crud_premium.get_premium(db, premium_id=request.premium_id)
    if not premium:
        raise HTTPException(status_code=404, detail="Premium not found")

    try:
        if not (premium.policy and premium.policy.user):
            raise HTTPException(status_code=404, detail="Policy is not linked to a user.")

        user = premium.policy.user
        
        # Step 1: Get or create a virtual account for the user.
        user_va = crud_virtual_account.get_virtual_account_by_user(db, user_id=user.id)
        if not user_va:
            logger.warning(f"No VA found for user {user.id}. Creating one...")
            va_creation_result = await virtual_account_service.create_individual_virtual_account(
                db=db, user=user, policy_id=premium.policy.id
            )
            if va_creation_result.get("success"):
                user_va = crud_virtual_account.get_virtual_account_by_user(db, user_id=user.id)
            else:
                error_msg = f"Failed to create VA for user {user.id}: {va_creation_result.get('error')}"
                logger.error(error_msg)
                raise HTTPException(status_code=500, detail=error_msg)

        if not user_va:
            raise HTTPException(status_code=404, detail="Virtual account for user could not be found or created.")

        # Step 2: Simulate the payment to the user's virtual account.
        logger.info(f"--- 🧪 Stage 1: Simulating payment of ₦{premium.amount} to user's VA {user_va.virtual_account_number} ---")
        payment_result = await squad_co_service.simulate_payment(
            virtual_account_number=user_va.virtual_account_number,
            amount=premium.amount
        )

        # Ensure payment_result is a dictionary
        if not isinstance(payment_result, dict):
            error_msg = f"Unexpected response type from payment simulation: {type(payment_result)}. Response: {payment_result}"
            logger.error(error_msg)
            raise HTTPException(status_code=500, detail=error_msg)

        if not payment_result.get("success"):
            raise HTTPException(status_code=400, detail=payment_result.get("message", "Failed to simulate payment to user's virtual account"))
        
        # Step 3: Manually update the VA balance and policy status (simulating the webhook).
        logger.info(f"--- 🧪 Simulating webhook processing: Updating balances and policy status... ---")
        crud_virtual_account.update_virtual_account_balance(db, virtual_account_id=user_va.id, credit_amount=premium.amount)
        
        # Correctly call the status update function with the required arguments
        transaction_ref = "simulated_ref"
        if isinstance(payment_result, dict) and "data" in payment_result:
            transaction_ref = payment_result.get("data", {}).get("transaction_reference", "simulated_ref")
        crud_policy.update_policy_payment_status(
            db, 
            merchant_ref=premium.policy.merchant_reference, 
            status="paid", 
            tx_ref=transaction_ref
        )

        # Step 4: Trigger the settlement.
        logger.info(f"--- 🧪 Stage 2: Triggering settlement from user's VA to insurance firm... ---")
        settlement_result = await settlement_service.process_settlement(db, virtual_account_id=user_va.id)
        if settlement_result.get("error"):
            logger.error(f"Settlement processing failed: {settlement_result.get('error')}")
            return {
                "message": "Payment simulation successful, but automated settlement failed.",
                "details": {"payment": payment_result, "settlement": settlement_result}
            }
            
        return {
            "message": "Full payment and settlement flow simulated successfully.",
            "details": {"payment": payment_result, "settlement": settlement_result}
        }

    except Exception as e:
        logger.error(f"An unexpected error occurred during the simulation: {e}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test-create-va", response_model=dict, tags=["Testing"])
async def test_create_va(
    request: TestVAAccountCreationRequest,
    db: Session = Depends(get_db)
):
    """Creates a virtual account for a specific user."""
    logger.info(f"--- 🧪 Test: Create VA for User ID: {request.user_id} ---")
    user = crud_user.get_user_by_id(db, user_id=request.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    result = await virtual_account_service.create_individual_virtual_account(db=db, user=user)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to create VA"))
    return result

@router.post("/test-fund-va", response_model=dict, tags=["Testing"])
async def test_fund_va(request: TestVAFundingRequest):
    """Simulates a payment to a specific virtual account."""
    logger.info(f"--- 🧪 Test: Fund VA {request.virtual_account_number} with ₦{request.amount} ---")
    result = await squad_co_service.simulate_payment(
        virtual_account_number=request.virtual_account_number,
        amount=request.amount
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message", "Failed to fund VA"))
    return result

@router.post("/test-transfer-va", response_model=dict, tags=["Testing"])
async def test_transfer_va(request: TestVATransferRequest):
    """Initiates a transfer between two virtual accounts."""
    logger.info(f"--- 🧪 Test: Transfer ₦{request.amount} from {request.from_account} to {request.to_account} ---")
    
    # For sandbox testing, a "transfer" between VAs is simulated by crediting the destination account.
    # This uses the same logic as the "Fund VA" step, which is the correct approach according to Squad's docs.
    result = await squad_co_service.simulate_payment(
        virtual_account_number=request.to_account,
        amount=request.amount
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message", "Failed to transfer to VA"))
    return result
