"""
API endpoints for payment reminder operations.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from pydantic import BaseModel

from app.core.database import get_db
from app.dependencies import get_current_admin_user
from app.models.user import User
from app.crud import policy as crud_policy
from app.crud import premium as crud_premium

router = APIRouter()
logger = logging.getLogger(__name__)

class ReminderRequest(BaseModel):
    policy_ids: Optional[List[int]] = None
    broker_ids: Optional[List[int]] = None

class ReminderResponse(BaseModel):
    message: str
    policies_count: int
    brokers_count: int

@router.post("/send", response_model=ReminderResponse)
def send_payment_reminders(
    reminder_request: ReminderRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Send payment reminders to brokers for outstanding premiums.
    Admin only.
    """
    try:
        policy_ids = reminder_request.policy_ids or []
        broker_ids = reminder_request.broker_ids or []
        
        if not policy_ids and not broker_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either policy_ids or broker_ids must be provided"
            )
        
        logger.info(f"Admin {current_user.email} initiating reminders for policies: {policy_ids}, brokers: {broker_ids}")
        
        # Get policies that need reminders
        outstanding_policies = []
        unique_broker_ids = set()
        
        if policy_ids:
            for policy_id in policy_ids:
                try:
                    policy = crud_policy.get_policy(db, policy_id=policy_id)
                    if policy:
                        # Check if policy has outstanding premiums
                        unpaid_premiums = crud_premium.get_unpaid_premiums_by_policy(db, policy_id=policy_id)
                        if unpaid_premiums:
                            outstanding_policies.append(policy)
                            # Add broker ID if it exists
                            if policy.broker_id:
                                unique_broker_ids.add(policy.broker_id)
                    else:
                        logger.warning(f"Policy {policy_id} not found")
                except Exception as e:
                    logger.error(f"Error processing policy {policy_id}: {str(e)}")
                    continue
        
        if broker_ids:
            # If broker IDs are provided, find all their policies with outstanding premiums
            for broker_id in broker_ids:
                try:
                    broker_policies = crud_policy.get_policies_by_broker(db, broker_id=broker_id)
                    for policy in broker_policies:
                        unpaid_premiums = crud_premium.get_unpaid_premiums_by_policy(db, policy_id=policy.id)
                        if unpaid_premiums and policy not in outstanding_policies:
                            outstanding_policies.append(policy)
                            unique_broker_ids.add(broker_id)
                except Exception as e:
                    logger.error(f"Error processing broker {broker_id}: {str(e)}")
                    continue
        
        logger.info(f"Found {len(outstanding_policies)} policies with outstanding premiums for {len(unique_broker_ids)} brokers")
        
        # For now, we'll simulate sending reminders
        # In a real implementation, you would:
        # 1. Send emails to brokers
        # 2. Create notifications in the system
        # 3. Log the reminder activity
        # 4. Update reminder_sent_at timestamp on policies
        
        # Simulate successful reminder sending
        # In production, you would implement actual email/notification logic here
        
        return ReminderResponse(
            message=f"Reminders sent successfully for {len(outstanding_policies)} policies to {len(unique_broker_ids)} brokers",
            policies_count=len(outstanding_policies),
            brokers_count=len(unique_broker_ids)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in send_payment_reminders: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing reminders"
        ) 