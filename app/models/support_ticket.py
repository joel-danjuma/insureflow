"""
Support Ticket model for InsureFlow application.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class TicketStatus(enum.Enum):
    """Support ticket status enumeration."""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class TicketPriority(enum.Enum):
    """Support ticket priority enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TicketCategory(enum.Enum):
    """Support ticket category enumeration."""
    GENERAL = "general"
    POLICIES = "policies"
    PAYMENTS = "payments"
    COMMISSIONS = "commissions"
    TECHNICAL = "technical"


class SupportTicket(Base):
    """Support ticket model for broker support requests."""
    
    __tablename__ = "support_tickets"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Ticket information
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False, default=TicketCategory.GENERAL.value)
    
    # Status and priority
    status = Column(
        String(50), 
        nullable=False, 
        default=TicketStatus.OPEN.value,
        index=True
    )
    priority = Column(
        String(50), 
        nullable=False, 
        default=TicketPriority.MEDIUM.value,
        index=True
    )
    
    # User who created the ticket (broker)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Admin response and assignment
    admin_response = Column(Text, nullable=True)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    resolved_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], backref="support_tickets")
    assigned_admin = relationship("User", foreign_keys=[assigned_to])
    
    def mark_as_resolved(self):
        """Mark ticket as resolved."""
        if self.status != TicketStatus.RESOLVED.value:
            self.status = TicketStatus.RESOLVED.value
            self.resolved_at = datetime.utcnow()
    
    def close_ticket(self):
        """Close ticket."""
        if self.status != TicketStatus.CLOSED.value:
            self.status = TicketStatus.CLOSED.value
            if not self.resolved_at:
                self.resolved_at = datetime.utcnow()
    
    def __repr__(self):
        return f"<SupportTicket(id={self.id}, user_id={self.user_id}, title='{self.title}', status='{self.status}')>"

