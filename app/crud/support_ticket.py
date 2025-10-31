"""
CRUD operations for the SupportTicket model.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy import and_

from app.models.support_ticket import SupportTicket, TicketStatus, TicketPriority, TicketCategory


def create_support_ticket(
    db: Session,
    user_id: int,
    title: str,
    description: str,
    category: str = TicketCategory.GENERAL.value,
    priority: str = TicketPriority.MEDIUM.value
) -> SupportTicket:
    """
    Create a new support ticket.
    """
    ticket = SupportTicket(
        user_id=user_id,
        title=title,
        description=description,
        category=category,
        priority=priority,
        status=TicketStatus.OPEN.value
    )
    
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def get_user_tickets(
    db: Session,
    user_id: int,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[SupportTicket]:
    """
    Get support tickets for a specific user.
    """
    query = db.query(SupportTicket).filter(
        SupportTicket.user_id == user_id
    )
    
    if status:
        query = query.filter(SupportTicket.status == status)
    
    return query.order_by(SupportTicket.created_at.desc()).offset(skip).limit(limit).all()


def get_ticket_by_id(
    db: Session,
    ticket_id: int,
    user_id: Optional[int] = None
) -> Optional[SupportTicket]:
    """
    Get a support ticket by ID.
    If user_id is provided, only return ticket if it belongs to that user.
    """
    query = db.query(SupportTicket).filter(SupportTicket.id == ticket_id)
    
    if user_id:
        query = query.filter(SupportTicket.user_id == user_id)
    
    return query.first()


def get_all_tickets(
    db: Session,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[SupportTicket]:
    """
    Get all support tickets (admin only).
    Supports filtering by status, priority, and category.
    """
    query = db.query(SupportTicket)
    
    # Only filter if value is provided and not empty (after stripping whitespace)
    if status and status.strip():
        query = query.filter(SupportTicket.status == status.strip().lower())
    if priority and priority.strip():
        query = query.filter(SupportTicket.priority == priority.strip().lower())
    if category and category.strip():
        query = query.filter(SupportTicket.category == category.strip().lower())
    
    return query.order_by(SupportTicket.created_at.desc()).offset(skip).limit(limit).all()


def update_ticket_status(
    db: Session,
    ticket_id: int,
    status: str,
    admin_id: Optional[int] = None
) -> Optional[SupportTicket]:
    """
    Update the status of a support ticket.
    """
    ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
    
    if not ticket:
        return None
    
    ticket.status = status
    ticket.updated_at = datetime.utcnow()
    
    # Auto-assign if status changes to in_progress and admin_id provided
    if status == TicketStatus.IN_PROGRESS.value and admin_id:
        ticket.assigned_to = admin_id
    
    # Mark as resolved if status is resolved
    if status == TicketStatus.RESOLVED.value:
        ticket.mark_as_resolved()
    
    # Close ticket if status is closed
    if status == TicketStatus.CLOSED.value:
        ticket.close_ticket()
    
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def add_admin_response(
    db: Session,
    ticket_id: int,
    admin_response: str,
    admin_id: Optional[int] = None
) -> Optional[SupportTicket]:
    """
    Add an admin response to a support ticket.
    """
    ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
    
    if not ticket:
        return None
    
    ticket.admin_response = admin_response
    ticket.updated_at = datetime.utcnow()
    
    # Auto-assign if not already assigned and admin_id provided
    if not ticket.assigned_to and admin_id:
        ticket.assigned_to = admin_id
    
    # Auto-update status to in_progress if it's still open
    if ticket.status == TicketStatus.OPEN.value:
        ticket.status = TicketStatus.IN_PROGRESS.value
        if admin_id:
            ticket.assigned_to = admin_id
    
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def get_ticket_count_by_status(
    db: Session,
    user_id: Optional[int] = None
) -> dict:
    """
    Get count of tickets by status.
    If user_id is provided, only count tickets for that user.
    """
    query = db.query(SupportTicket)
    
    if user_id:
        query = query.filter(SupportTicket.user_id == user_id)
    
    total = query.count()
    open_count = query.filter(SupportTicket.status == TicketStatus.OPEN.value).count()
    in_progress_count = query.filter(SupportTicket.status == TicketStatus.IN_PROGRESS.value).count()
    resolved_count = query.filter(SupportTicket.status == TicketStatus.RESOLVED.value).count()
    closed_count = query.filter(SupportTicket.status == TicketStatus.CLOSED.value).count()
    
    return {
        'total': total,
        'open': open_count,
        'in_progress': in_progress_count,
        'resolved': resolved_count,
        'closed': closed_count
    }

