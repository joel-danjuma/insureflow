"""
Service layer for notification-related operations.
"""
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from datetime import datetime, timedelta

from app.crud import notification as crud_notification
from app.crud import policy as crud_policy
from app.crud import premium as crud_premium
from app.models.policy import Policy
from app.models.premium import Premium
from app.models.notification import Notification

logger = logging.getLogger(__name__)


async def send_payment_reminders_to_brokers(
    db: Session,
    max_days_overdue: int = 30,
    reminder_cooldown_hours: int = 24
) -> dict:
    """
    High-level service to send payment reminders to brokers.
    
    This function:
    1. Finds all overdue policies (1-30 days past due)
    2. Filters out policies that had reminders sent recently
    3. Creates notifications for brokers
    4. Updates reminder timestamps on policies
    
    Returns summary of actions taken.
    """
    try:
        logger.info(f"Starting automatic payment reminder process (max {max_days_overdue} days overdue)")
        
        # Get overdue policies that need reminders
        overdue_policies = crud_notification.get_overdue_policies_without_recent_reminders(
            db=db,
            max_days_overdue=max_days_overdue,
            reminder_cooldown_hours=reminder_cooldown_hours
        )
        
        if not overdue_policies:
            logger.info("No overdue policies found that need reminders")
            return {
                "success": True,
                "message": "No overdue policies found that need reminders",
                "notifications_created": 0,
                "brokers_notified": 0,
                "policies_processed": 0,
                "reminders_sent": []
            }
        
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
        logger.info(f"AUTOMATIC REMINDERS COMPLETE: {success_message}")
        
        return {
            "success": True,
            "message": success_message,
            "notifications_created": notifications_created,
            "brokers_notified": len(brokers_notified),
            "policies_processed": len(overdue_policies),
            "reminders_sent": reminders_sent
        }
        
    except Exception as e:
        logger.error(f"Error in send_payment_reminders_to_brokers: {str(e)}")
        db.rollback()
        return {
            "success": False,
            "message": f"Failed to send payment reminders: {str(e)}",
            "notifications_created": 0,
            "brokers_notified": 0,
            "policies_processed": 0,
            "reminders_sent": []
        }


def get_broker_notification_summary(db: Session, broker_id: int) -> dict:
    """
    Get a summary of notifications for a broker.
    """
    try:
        unread_count = crud_notification.get_unread_count(db, broker_id)
        recent_notifications = crud_notification.get_broker_notifications(
            db, broker_id, unread_only=False, limit=5
        )
        
        return {
            "broker_id": broker_id,
            "unread_count": unread_count,
            "total_recent": len(recent_notifications),
            "has_urgent": any(
                "overdue" in notif.title.lower() and not notif.is_read 
                for notif in recent_notifications
            )
        }
    except Exception as e:
        logger.error(f"Error getting notification summary for broker {broker_id}: {str(e)}")
        return {
            "broker_id": broker_id,
            "unread_count": 0,
            "total_recent": 0,
            "has_urgent": False,
            "error": str(e)
        }


def cleanup_old_notifications(db: Session, days_old: int = 30) -> int:
    """
    Clean up old dismissed notifications.
    """
    try:
        deleted_count = crud_notification.cleanup_old_notifications(db, days_old)
        logger.info(f"Cleaned up {deleted_count} old notifications (older than {days_old} days)")
        return deleted_count
    except Exception as e:
        logger.error(f"Error cleaning up notifications: {str(e)}")
        return 0


def test_notification_system(db: Session) -> dict:
    """
    Test function to verify the notification system is working.
    Creates a test notification for debugging.
    """
    try:
        # Find any broker to test with
        test_policy = db.query(Policy).filter(
            Policy.broker_id.isnot(None)
        ).first()
        
        if not test_policy or not test_policy.broker:
            return {
                "success": False,
                "message": "No policies with brokers found for testing"
            }
        
        # Create a test notification
        test_notification = crud_notification.create_payment_reminder_notification(
            db=db,
            broker_id=test_policy.broker.user_id,
            policy_id=test_policy.id,
            outstanding_amount=50000.00,
            days_overdue=15,
            policy_number=test_policy.policy_number,
            customer_name="Test Customer"
        )
        
        return {
            "success": True,
            "message": f"Test notification created successfully",
            "notification_id": test_notification.id,
            "broker_name": test_policy.broker.name,
            "policy_number": test_policy.policy_number
        }
        
    except Exception as e:
        logger.error(f"Error testing notification system: {str(e)}")
        return {
            "success": False,
            "message": f"Test failed: {str(e)}"
        } 