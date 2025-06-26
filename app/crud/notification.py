"""
CRUD operations for the Notification model.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from sqlalchemy import func, and_

from app.models.notification import Notification, NotificationType
from app.models.user import User, UserRole
from app.models.policy import Policy
from app.models.broker import Broker
from app.models.premium import Premium, PremiumPaymentStatus


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
    This is an optimized query that performs calculations in the database.
    Uses PostgreSQL-compatible date functions.
    Returns tuples of (policy, broker, customer, days_overdue, outstanding_amount).
    """
    now = datetime.utcnow()
    reminder_cooldown_date = now - timedelta(hours=reminder_cooldown_hours)
    
    # Subquery to calculate outstanding amounts and filter for unpaid premiums
    outstanding_subquery = db.query(
        Premium.policy_id,
        func.sum(Premium.outstanding_amount).label("total_outstanding")
    ).filter(
        Premium.payment_status != PremiumPaymentStatus.PAID
    ).group_by(Premium.policy_id).subquery()

    # Calculate days overdue using PostgreSQL-compatible functions
    days_overdue_expr = func.current_date() - Policy.end_date

    # Main query to get overdue policies
    query = db.query(
        Policy,
        Broker,
        User,
        days_overdue_expr.label("days_overdue"),
        outstanding_subquery.c.total_outstanding
    ).join(
        Broker, Policy.broker_id == Broker.id
    ).join(
        User, Policy.user_id == User.id
    ).join(
        outstanding_subquery, Policy.id == outstanding_subquery.c.policy_id
    ).filter(
        # Policy is active
        Policy.status == "active",
        # Policy is associated with a broker
        Policy.broker_id.isnot(None),
        # User is a customer (not an admin or broker policy)
        User.role == UserRole.CUSTOMER,
        # Outstanding amount is greater than 0
        outstanding_subquery.c.total_outstanding > 0,
        # Policy is overdue but not more than max_days_overdue
        and_(
            days_overdue_expr > 0,
            days_overdue_expr <= max_days_overdue
        ),
        # Reminder has not been sent recently (or ever)
        (Policy.reminder_sent_at.is_(None) | (Policy.reminder_sent_at < reminder_cooldown_date))
    )
    
    return query.all()


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