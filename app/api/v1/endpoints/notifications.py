"""
API endpoints for broker notification management.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging
from pydantic import BaseModel

from app.core.database import get_db
from app.dependencies import get_current_broker_user
from app.models.user import User
from app.crud import notification as crud_notification

router = APIRouter()
logger = logging.getLogger(__name__)

class NotificationResponse(BaseModel):
    id: int
    type: str
    title: str
    message: str
    policy_id: int | None
    is_read: bool
    is_dismissed: bool
    created_at: str
    
    class Config:
        from_attributes = True

class NotificationSummary(BaseModel):
    total_unread: int
    notifications: List[NotificationResponse]

@router.get("/", response_model=NotificationSummary)
def get_broker_notifications(
    unread_only: bool = False,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_broker_user)
):
    """
    Get payment reminder notifications for the current broker.
    Only brokers can access this endpoint.
    """
    try:
        # Get notifications for this broker
        notifications = crud_notification.get_broker_notifications(
            db=db,
            broker_id=current_user.id,
            unread_only=unread_only,
            limit=limit
        )
        
        # Get unread count
        unread_count = crud_notification.get_unread_count(
            db=db,
            broker_id=current_user.id
        )
        
        # Convert to response format
        notification_responses = []
        for notification in notifications:
            notification_responses.append(NotificationResponse(
                id=notification.id,
                type=notification.type,
                title=notification.title,
                message=notification.message,
                policy_id=notification.policy_id,
                is_read=notification.is_read,
                is_dismissed=notification.is_dismissed,
                created_at=notification.created_at.isoformat()
            ))
        
        return NotificationSummary(
            total_unread=unread_count,
            notifications=notification_responses
        )
        
    except Exception as e:
        logger.error(f"Error fetching notifications for broker {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching notifications"
        )

@router.post("/{notification_id}/read")
def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_broker_user)
):
    """
    Mark a notification as read.
    Only the notification owner (broker) can mark it as read.
    """
    try:
        notification = crud_notification.mark_notification_as_read(
            db=db,
            notification_id=notification_id,
            broker_id=current_user.id
        )
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found or you don't have permission to access it"
            )
        
        return {"message": "Notification marked as read", "notification_id": notification_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking notification {notification_id} as read: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the notification"
        )

@router.post("/{notification_id}/dismiss")
def dismiss_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_broker_user)
):
    """
    Dismiss a notification (removes it from the list).
    Only the notification owner (broker) can dismiss it.
    """
    try:
        notification = crud_notification.dismiss_notification(
            db=db,
            notification_id=notification_id,
            broker_id=current_user.id
        )
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found or you don't have permission to access it"
            )
        
        return {"message": "Notification dismissed", "notification_id": notification_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error dismissing notification {notification_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while dismissing the notification"
        )

@router.get("/unread-count")
def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_broker_user)
):
    """
    Get the count of unread notifications for the current broker.
    """
    try:
        count = crud_notification.get_unread_count(
            db=db,
            broker_id=current_user.id
        )
        
        return {"unread_count": count}
        
    except Exception as e:
        logger.error(f"Error getting unread count for broker {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching unread count"
        ) 