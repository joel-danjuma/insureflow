"""
API endpoints for payment reminder operations.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from pydantic import BaseModel
from datetime import datetime

from app.core.database import get_db
from app.dependencies import get_current_broker_or_admin_user
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
    reminders_sent: List[dict] = []

@router.post("/send", response_model=ReminderResponse)
def send_payment_reminders(
    reminder_request: ReminderRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_broker_or_admin_user)
):
    """
    Send payment reminders to brokers for outstanding premiums.
    Brokers can only send reminders for their own policies.
    Admins can send reminders for any policies.
    """
    try:
        policy_ids = reminder_request.policy_ids or []
        broker_ids = reminder_request.broker_ids or []
        
        # If user is a broker, restrict to their own policies only
        if current_user.role == "broker":
            # Get broker's own policies
            broker_policies = crud_policy.get_policies_by_broker(db, broker_id=current_user.id)
            broker_policy_ids = [p.id for p in broker_policies]
            
            # Filter policy_ids to only include broker's own policies
            if policy_ids:
                policy_ids = [pid for pid in policy_ids if pid in broker_policy_ids]
            else:
                policy_ids = broker_policy_ids
            
            # For brokers, ignore broker_ids parameter and only use their own ID
            broker_ids = [current_user.id]
            
            logger.info(f"Broker {current_user.email} sending reminders for {len(policy_ids)} of their own policies")
        else:
            # Admin user - can send reminders for any policies
            logger.info(f"Admin {current_user.email} initiating reminders for policies: {policy_ids}, brokers: {broker_ids}")
        
        if not policy_ids and not broker_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either policy_ids or broker_ids must be provided"
            )
        
        # Get policies that need reminders
        outstanding_policies = []
        unique_broker_ids = set()
        reminders_sent = []
        
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
                                
                                # Update reminder_sent_at timestamp
                                policy.reminder_sent_at = datetime.utcnow()
                                db.add(policy)
                                
                                # Log the reminder
                                total_outstanding = sum(p.outstanding_amount for p in unpaid_premiums)
                                reminders_sent.append({
                                    "policy_id": policy.id,
                                    "policy_number": policy.policy_number,
                                    "broker_name": policy.broker.name if policy.broker else "Unknown",
                                    "customer_name": policy.user.full_name if policy.user else "Unknown",
                                    "outstanding_amount": float(total_outstanding),
                                    "unpaid_premiums_count": len(unpaid_premiums),
                                    "sent_at": datetime.utcnow().isoformat()
                                })
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
                            
                            # Update reminder_sent_at timestamp
                            policy.reminder_sent_at = datetime.utcnow()
                            db.add(policy)
                            
                            # Log the reminder
                            total_outstanding = sum(p.outstanding_amount for p in unpaid_premiums)
                            reminders_sent.append({
                                "policy_id": policy.id,
                                "policy_number": policy.policy_number,
                                "broker_name": policy.broker.name if policy.broker else "Unknown",
                                "customer_name": policy.user.full_name if policy.user else "Unknown",
                                "outstanding_amount": float(total_outstanding),
                                "unpaid_premiums_count": len(unpaid_premiums),
                                "sent_at": datetime.utcnow().isoformat()
                            })
                except Exception as e:
                    logger.error(f"Error processing broker {broker_id}: {str(e)}")
                    continue
        
        # Commit the reminder timestamps
        db.commit()
        
        logger.info(f"Found {len(outstanding_policies)} policies with outstanding premiums for {len(unique_broker_ids)} brokers")
        
        # In a real implementation, you would:
        # 1. Send emails to brokers using an email service
        # 2. Create notifications in the system
        # 3. Send SMS reminders if phone numbers are available
        # 4. Schedule follow-up reminders
        
        success_message = f"Reminders logged successfully for {len(outstanding_policies)} policies to {len(unique_broker_ids)} brokers"
        
        # For now, we log the reminders but don't actually send emails
        # This could be extended to integrate with an email service like SendGrid, AWS SES, etc.
        logger.info(f"REMINDER SYSTEM: {success_message}")
        for reminder in reminders_sent:
            logger.info(f"REMINDER: Policy {reminder['policy_number']} - {reminder['broker_name']} - ₦{reminder['outstanding_amount']:,}")
        
        return ReminderResponse(
            message=success_message,
            policies_count=len(outstanding_policies),
            brokers_count=len(unique_broker_ids),
            reminders_sent=reminders_sent
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in send_payment_reminders: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing reminders"
        ) 