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
from app.schemas.testing import TestVAAccountCreationRequest, FullPaymentFlowTestResponse
from app.services.virtual_account_service import virtual_account_service

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/test-direct-va-creation", response_model=dict, tags=["Testing"])
async def test_direct_va_creation(
    request: TestVAAccountCreationRequest,
    db: Session = Depends(get_db)
):
    """
    Directly tests the virtual account creation service with a specific payload.
    This provides a clear and direct way to test the service logic.
    """
    logger.info(f"--- 📥 Received Direct VA Creation Request ---")
    logger.info(f"--- 📋 Payload: {request.model_dump_json(indent=2)} ---")

    try:
        # Step 1: Find the user specified in the request
        target_user = crud_user.get_user_by_id(db, user_id=request.user_id)
        if not target_user:
            logger.error(f"--- 🛑 FAILURE: User with ID {request.user_id} not found. ---")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Target user with ID {request.user_id} not found."
            )
        
        logger.info(f"--- ✅ Found user: {target_user.email} ---")

        # Step 2: Call the virtual account service with the found user
        result = await virtual_account_service.create_individual_virtual_account(
            db=db,
            user=target_user
        )

        # Step 3: Handle the result from the service
        if result.get("success"):
            logger.info(f"--- 🎉 SUCCESS: Virtual account created for {target_user.email}. ---")
            return {
                "success": True,
                "message": "Direct virtual account creation test successful.",
                "virtual_account": result.get("virtual_account")
            }
        else:
            error_message = result.get("error", "An unknown error occurred in the service")
            logger.error(f"--- 🛑 FAILURE: Service failed for {target_user.email}. Error: {error_message} ---")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message
            )

    except HTTPException:
        # Re-raise HTTP exceptions to let FastAPI handle them
        raise
    except Exception as e:
        logger.error(f"--- 💥 FATAL: An unexpected server error occurred: {str(e)} ---", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected server error occurred: {str(e)}"
        )

@router.post("/test-full-payment-flow", response_model=FullPaymentFlowTestResponse, tags=["Testing"])
async def test_full_payment_flow(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_broker_or_admin_user)
):
    """
    Tests the end-to-end payment flow:
    1. Creates a virtual account for the current user.
    2. Simulates a payment of 5000 NGN to that account.
    """
    logger.info(f"--- 🧪 Starting Full Payment Flow Test for User: {current_user.email} ---")

    try:
        # --- Step 1: Create Virtual Account ---
        logger.info("--- Step 1: Creating Virtual Account ---")
        va_creation_result = await virtual_account_service.create_individual_virtual_account(
            db=db,
            user=current_user
        )

        if not va_creation_result.get("success"):
            error_message = va_creation_result.get("error", "Failed to create virtual account")
            logger.error(f"--- 🛑 FAILURE (Step 1): {error_message} ---")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_message)

        virtual_account = va_creation_result.get("virtual_account")
        account_number = virtual_account.get("account_number")
        logger.info(f"--- ✅ SUCCESS (Step 1): Virtual account created: {account_number} ---")

        # --- Step 2: Simulate Payment ---
        logger.info(f"--- Step 2: Simulating Payment to {account_number} ---")
        test_amount = Decimal("5000.00")
        payment_sim_result = await virtual_account_service.simulate_payment(
            virtual_account_number=account_number,
            amount=test_amount
        )

        if not payment_sim_result.get("success"):
            error_message = payment_sim_result.get("error", "Failed to simulate payment")
            logger.error(f"--- 🛑 FAILURE (Step 2): {error_message} ---")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_message)

        logger.info(f"--- ✅ SUCCESS (Step 2): Payment of {test_amount} NGN simulated successfully. ---")
        
        # --- Final Success ---
        logger.info(f"--- 🎉 SUCCESS: Full payment flow test completed for {current_user.email} ---")
        return {
            "success": True,
            "message": "Full payment flow test completed successfully.",
            "virtual_account_details": virtual_account,
            "payment_simulation_details": payment_sim_result
        }

    except HTTPException:
        # Re-raise HTTP exceptions to let FastAPI handle them
        raise
    except Exception as e:
        logger.error(f"--- 💥 FATAL: An unexpected error occurred during the full payment flow test: {str(e)} ---", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected server error occurred: {str(e)}"
        )
