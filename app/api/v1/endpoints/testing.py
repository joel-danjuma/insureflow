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
from app.schemas.testing import TestVAAccountCreationRequest
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
