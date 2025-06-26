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
from app.dependencies import get_current_admin_user  # Admin-only now
from app.models.user import User
from app.crud import notification as crud_notification

router = APIRouter()
logger = logging.getLogger(__name__)

class AutoReminderRequest(BaseModel):
    max_days_overdue: Optional[int] = 30
    reminder_cooldown_hours: Optional[int] = 24

class ManualReminderRequest(BaseModel):
    broker_ids: Optional[List[int]] = None
    policy_ids: Optional[List[int]] = None

class ReminderResponse(BaseModel):
    message: str
    notifications_created: int
    brokers_notified: int
    policies_processed: int
    reminders_sent: List[dict] = []

@router.post("/send-auto", response_model=ReminderResponse)
def send_automatic_payment_reminders(
    request: AutoReminderRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)  # Admin only
):
    """
    Automatically detect and send payment reminders for overdue policies.
    Only insurance firm admins can send reminders.
    
    - Finds policies overdue up to 30 days (configurable)
    - Skips policies that had reminders sent recently (24h cooldown)
    - Creates notifications in broker dashboards
    - Updates reminder_sent_at timestamps
    """
    try:
        logger.info(f"Admin {current_user.email} initiating automatic payment reminders")
        
        # Get overdue policies that need reminders
        overdue_policies = crud_notification.get_overdue_policies_without_recent_reminders(
            db=db,
            max_days_overdue=request.max_days_overdue,
            reminder_cooldown_hours=request.reminder_cooldown_hours
        )
        
        if not overdue_policies:
            return ReminderResponse(
                message="No overdue policies found that need reminders",
                notifications_created=0,
                brokers_notified=0,
                policies_processed=0,
                reminders_sent=[]
            )
        
        notifications_created = 0
        brokers_notified = set()
        reminders_sent = []
        
        for policy, broker, customer, days_overdue, outstanding_amount in overdue_policies:
            try:
                # Create notification for the broker
                notification = crud_notification.create_payment_reminder_notification(
                    db=db,
                    broker_id=broker.user_id,  # Broker's user ID
                    policy_id=policy.id,
                    outstanding_amount=outstanding_amount,
                    days_overdue=days_overdue,
                    policy_number=policy.policy_number,
                    customer_name=customer.full_name
                )
                
                # Update policy reminder timestamp
                policy.reminder_sent_at = datetime.utcnow()
                db.add(policy)
                
                notifications_created += 1
                brokers_notified.add(broker.user_id)
                
                reminders_sent.append({
                    "policy_id": policy.id,
                    "policy_number": policy.policy_number,
                    "broker_name": broker.name,
                    "customer_name": customer.full_name,
                    "outstanding_amount": outstanding_amount,
                    "days_overdue": days_overdue,
                    "notification_id": notification.id,
                    "sent_at": datetime.utcnow().isoformat()
                })
                
                logger.info(f"Created reminder notification for policy {policy.policy_number} -> broker {broker.name}")
                
            except Exception as e:
                logger.error(f"Error creating reminder for policy {policy.id}: {str(e)}")
                continue
        
        # Commit all changes
        db.commit()
        
        success_message = f"Created {notifications_created} payment reminder notifications for {len(brokers_notified)} brokers"
        logger.info(f"AUTOMATIC REMINDERS: {success_message}")
        
        return ReminderResponse(
            message=success_message,
            notifications_created=notifications_created,
            brokers_notified=len(brokers_notified),
            policies_processed=len(overdue_policies),
            reminders_sent=reminders_sent
        )
        
    except Exception as e:
        logger.error(f"Unexpected error in send_automatic_payment_reminders: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing automatic reminders"
        )


@router.post("/send-manual", response_model=ReminderResponse)
def send_manual_payment_reminders(
    request: ManualReminderRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)  # Admin only
):
    """
    Manually send payment reminders for specific brokers or policies.
    Only insurance firm admins can send reminders.
    """
    try:
        logger.info(f"Admin {current_user.email} sending manual reminders for brokers: {request.broker_ids}, policies: {request.policy_ids}")
        
        if not request.broker_ids and not request.policy_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either broker_ids or policy_ids must be provided"
            )
        
        # Implementation similar to automatic but for specific brokers/policies
        # This would be a more targeted version of the automatic system
        
        return ReminderResponse(
            message="Manual reminders feature will be implemented based on automatic reminders",
            notifications_created=0,
            brokers_notified=0,
            policies_processed=0,
            reminders_sent=[]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in send_manual_payment_reminders: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing manual reminders"
        )


# Keep the old endpoint for backward compatibility but make it redirect to auto
@router.post("/send", response_model=ReminderResponse)
def send_payment_reminders_legacy(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Legacy endpoint - redirects to automatic reminders.
    Only admins can send reminders now.
    """
    request = AutoReminderRequest()
    return send_automatic_payment_reminders(request, db, current_user) 