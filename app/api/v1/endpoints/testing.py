"""
Testing API endpoints for payment flow simulation and stakeholder demonstrations.
Provides comprehensive logging and real-time feedback for dashboard testing.
"""
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.dependencies import get_current_broker_or_admin_user
from app.models.user import User
from app.crud import user as crud_user
from app.schemas.testing import (
    TestVAAccountCreationRequest, 
    TestVAFundingRequest, 
    TestVATransferRequest
)
from app.services.virtual_account_service import virtual_account_service
from app.services.squad_co import squad_co_service

logger = logging.getLogger(__name__)
router = APIRouter()

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
    
    # Note: This uses the standard bank transfer endpoint, assuming VAs can be used.
    # The payload structure is based on Squad's transfer documentation.
    payload = {
        "bank_code": "000000", # Placeholder, assuming Squad handles VA-to-VA internally
        "account_number": request.to_account,
        "amount": int(request.amount * 100), # Amount in kobo
        "remark": f"Test transfer from {request.from_account}"
    }
    
    # This is a conceptual implementation. We may need to adjust the payload 
    # based on how Squad's API handles transfers between VAs they provisioned.
    # The `from_account` would likely be identified by the API key's scope.
    
    result = await squad_co_service.initiate_transfer(payload)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message", "Transfer failed"))
    return result
