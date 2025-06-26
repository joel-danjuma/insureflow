"""
Notification model for InsureFlow application.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class NotificationType(enum.Enum):
    """Notification type enumeration."""
    PAYMENT_REMINDER = "payment_reminder"
    SYSTEM_ALERT = "system_alert"
    POLICY_UPDATE = "policy_update"


class Notification(Base):
    """Notification model for broker dashboard notifications."""
    
    __tablename__ = "notifications"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Recipient
    broker_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Notification details
    type = Column(String(50), nullable=False, default=NotificationType.PAYMENT_REMINDER.value)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    
    # Related entities
    policy_id = Column(Integer, ForeignKey("policies.id"), nullable=True, index=True)
    
    # Status
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    is_dismissed = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    read_at = Column(DateTime, nullable=True)
    dismissed_at = Column(DateTime, nullable=True)
    
    # Relationships
    broker = relationship("User", back_populates="notifications", foreign_keys=[broker_id])
    policy = relationship("Policy", back_populates="notifications")
    
    def mark_as_read(self):
        """Mark notification as read."""
        if not self.is_read:
            self.is_read = True
            self.read_at = datetime.utcnow()
    
    def dismiss(self):
        """Dismiss notification."""
        if not self.is_dismissed:
            self.is_dismissed = True
            self.dismissed_at = datetime.utcnow()
    
    def __repr__(self):
        return f"<Notification(id={self.id}, broker_id={self.broker_id}, type='{self.type}', title='{self.title}')>" 