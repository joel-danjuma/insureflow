"""
CRUD operations for the Notification model.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.models.notification import Notification, NotificationType
from app.models.user import User
from app.models.policy import Policy


def create_payment_reminder_notification(
    db: Session,
    broker_id: int,
    policy_id: int,
    outstanding_amount: float,
    days_overdue: int,
    policy_number: str,
    customer_name: str
) -> Notification:
    """
    Create a payment reminder notification for a broker.
    """
    title = f"Payment Reminder - Policy {policy_number}"
    message = f"Policy {policy_number} for {customer_name} is {days_overdue} days overdue. Outstanding amount: ₦{outstanding_amount:,.2f}. Please follow up with the customer."
    
    notification = Notification(
        broker_id=broker_id,
        policy_id=policy_id,
        type=NotificationType.PAYMENT_REMINDER.value,
        title=title,
        message=message
    )
    
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def get_broker_notifications(
    db: Session,
    broker_id: int,
    unread_only: bool = False,
    limit: int = 50
) -> List[Notification]:
    """
    Get notifications for a specific broker.
    """
    query = db.query(Notification).filter(
        Notification.broker_id == broker_id,
        Notification.is_dismissed == False
    )
    
    if unread_only:
        query = query.filter(Notification.is_read == False)
    
    return query.order_by(Notification.created_at.desc()).limit(limit).all()


def mark_notification_as_read(db: Session, notification_id: int, broker_id: int) -> Optional[Notification]:
    """
    Mark a notification as read.
    """
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.broker_id == broker_id
    ).first()
    
    if notification:
        notification.mark_as_read()
        db.add(notification)
        db.commit()
        db.refresh(notification)
    
    return notification


def dismiss_notification(db: Session, notification_id: int, broker_id: int) -> Optional[Notification]:
    """
    Dismiss a notification.
    """
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.broker_id == broker_id
    ).first()
    
    if notification:
        notification.dismiss()
        db.add(notification)
        db.commit()
        db.refresh(notification)
    
    return notification


def get_unread_count(db: Session, broker_id: int) -> int:
    """
    Get count of unread notifications for a broker.
    """
    return db.query(Notification).filter(
        Notification.broker_id == broker_id,
        Notification.is_read == False,
        Notification.is_dismissed == False
    ).count()


def get_overdue_policies_without_recent_reminders(
    db: Session,
    max_days_overdue: int = 30,
    reminder_cooldown_hours: int = 24
) -> List[tuple]:
    """
    Get policies that are overdue but haven't had reminders sent recently.
    Returns tuples of (policy, broker, customer, days_overdue, outstanding_amount).
    """
    cutoff_date = datetime.utcnow() - timedelta(hours=reminder_cooldown_hours)
    
    # This is a simplified query - in practice, you'd want to join with premiums
    # to calculate actual outstanding amounts and overdue status
    overdue_policies = []
    
    # Get all policies with brokers
    policies = db.query(Policy).filter(
        Policy.broker_id.isnot(None),
        Policy.status == "active"
    ).all()
    
    for policy in policies:
        # Check if reminder was sent recently
        if policy.reminder_sent_at and policy.reminder_sent_at > cutoff_date:
            continue
        
        # Calculate if overdue (simplified - you might want more complex logic)
        days_past_end = (datetime.utcnow().date() - policy.end_date).days
        
        if 0 < days_past_end <= max_days_overdue:
            # Get outstanding amount from premiums
            outstanding_amount = 0
            if policy.premiums:
                for premium in policy.premiums:
                    if premium.payment_status.value != 'paid':
                        outstanding_amount += float(premium.outstanding_amount)
            
            if outstanding_amount > 0:
                overdue_policies.append((
                    policy,
                    policy.broker,
                    policy.user,
                    days_past_end,
                    outstanding_amount
                ))
    
    return overdue_policies


def cleanup_old_notifications(db: Session, days_old: int = 30) -> int:
    """
    Clean up old dismissed notifications.
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days_old)
    
    deleted_count = db.query(Notification).filter(
        Notification.is_dismissed == True,
        Notification.dismissed_at < cutoff_date
    ).delete()
    
    db.commit()
    return deleted_count 