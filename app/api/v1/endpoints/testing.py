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
from app.crud import user as crud_user, premium as crud_premium, virtual_account as crud_virtual_account
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
    Simulates a payment from a broker's test account to InsureFlow's settlement account.
    This mimics the first leg of the payment flow.
    """
    logger.info(f"--- 🧪 Test: Simulating payment for Premium ID: {request.premium_id} ---")

    premium = crud_premium.get_premium(db, premium_id=request.premium_id)
    if not premium:
        raise HTTPException(status_code=404, detail="Premium not found")

    amount = premium.amount

    logger.info(f"--- 🧪 Transferring ₦{amount} from {settings.BROKER_TEST_ACCOUNT_NUMBER} to {settings.INSUREFLOW_SETTLEMENT_ACCOUNT_NUMBER} ---")

    # In a real scenario with Squad Co's transfer API, you'd call it here.
    # Since we are simulating, and the core logic is covered by funding the settlement account,
    # we can re-use the simulate_payment function from squad_co_service for simplicity.
    # This effectively credits the settlement account, which is what the transfer would do.
    
    result = await squad_co_service.simulate_payment(
        virtual_account_number=settings.INSUREFLOW_SETTLEMENT_ACCOUNT_NUMBER,
        amount=float(amount)
    )

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message", "Failed to simulate payment to settlement account"))
    
    # --- Trigger settlement logic after successful payment ---
    logger.info(f"--- 🧪 Payment to settlement account successful. Triggering settlement to insurance firm... ---")
    try:
        # Correctly find the virtual account via the policy's user
        if premium.policy and premium.policy.user_id:
            # Find the virtual account linked to the user
            user_va = crud_virtual_account.get_virtual_account_by_user(db, user_id=premium.policy.user_id)
            if user_va:
                settlement_result = await settlement_service.process_settlement(db, virtual_account_id=user_va.id)
                if settlement_result.get("error"):
                     logger.error(f"Settlement processing failed: {settlement_result.get('error')}")
            else:
                logger.warning(f"Could not trigger settlement for premium {premium.id} because no virtual account is linked to the policy's user.")
        else:
            logger.warning(f"Could not trigger settlement for premium {premium.id} because no user is linked to the policy.")

    except Exception as e:
        logger.error(f"An unexpected error occurred during settlement trigger: {e}")

    return {
        "message": "Payment simulation successful. InsureFlow settlement account has been credited.",
        "details": result
    }

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
