"""
Testing API endpoints for payment flow simulation and stakeholder demonstrations.
Provides comprehensive logging and real-time feedback for dashboard testing.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.dependencies import get_current_broker_or_admin_user
from app.models.user import User, UserRole
from app.crud import user as crud_user
from app.services.virtual_account_service import virtual_account_service

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/create-test-virtual-account")
async def create_test_virtual_account(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_broker_or_admin_user)
):
    """
    Directly creates a test virtual account and logs the payload.
    """
    logger.info("--- Starting Direct Virtual Account Creation Test ---")
    try:
        # Step 1: Ensure a valid test user exists
        test_user_email = "test.broker@insureflow.com"
        test_user = crud_user.get_user_by_email(db, email=test_user_email)
        
        if not test_user:
            logger.info("Test broker user not found. Creating a new one.")
            from app.schemas.auth import UserCreate
            test_user = crud_user.create_user(db, user=UserCreate(
                email=test_user_email,
                full_name="Virtual Account Test Broker",
                username="vabroker",
                password="a-secure-password",
                role="BROKER"
            ))
            logger.info(f"Created new test user: {test_user.email}")
        else:
            logger.info(f"Found existing test user: {test_user.email}")

        # Step 2: Call the virtual account service directly
        result = await virtual_account_service.create_individual_virtual_account(
            db=db,
            user=test_user
        )

        # Step 3: Handle the result
        if result.get("success"):
            logger.info(f"SUCCESS: Virtual account created successfully. Response: {result}")
            return {
                "success": True,
                "virtual_account": result.get("virtual_account"),
                "message": "Test virtual account created successfully"
            }
        else:
            error_message = result.get("error", "An unknown error occurred")
            logger.error(f"FAILURE: Virtual account creation failed. Error: {error_message}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message
            )

    except Exception as e:
        logger.error(f"FATAL: An unexpected error occurred in the test endpoint: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )
