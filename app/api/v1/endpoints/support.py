"""
API endpoints for support ticket management.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.core.database import get_db
from app.dependencies import get_current_broker_user, get_current_insureflow_admin, get_current_active_user
from app.models.user import User
from app.crud import support_ticket as crud_support_ticket
from app.schemas import support_ticket as schemas_support_ticket

router = APIRouter()
logger = logging.getLogger(__name__)


# Broker endpoints
@router.post("/tickets", response_model=schemas_support_ticket.SupportTicketResponse, status_code=status.HTTP_201_CREATED)
def create_support_ticket(
    ticket_in: schemas_support_ticket.SupportTicketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_broker_user)
):
    """
    Create a new support ticket.
    Only brokers can create tickets.
    """
    try:
        ticket = crud_support_ticket.create_support_ticket(
            db=db,
            user_id=current_user.id,
            title=ticket_in.title,
            description=ticket_in.description,
            category=ticket_in.category,
            priority=ticket_in.priority
        )
        
        return schemas_support_ticket.SupportTicketResponse(
            id=ticket.id,
            title=ticket.title,
            description=ticket.description,
            category=ticket.category,
            status=ticket.status,
            priority=ticket.priority,
            user_id=ticket.user_id,
            admin_response=ticket.admin_response,
            assigned_to=ticket.assigned_to,
            created_at=ticket.created_at,
            updated_at=ticket.updated_at,
            resolved_at=ticket.resolved_at
        )
        
    except Exception as e:
        logger.error(f"Error creating support ticket for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the support ticket"
        )


@router.get("/tickets", response_model=List[schemas_support_ticket.SupportTicketResponse])
def get_user_tickets(
    status: Optional[str] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_broker_user)
):
    """
    Get support tickets for the current user.
    Only brokers can access this endpoint.
    """
    try:
        tickets = crud_support_ticket.get_user_tickets(
            db=db,
            user_id=current_user.id,
            status=status,
            skip=skip,
            limit=limit
        )
        
        return [
            schemas_support_ticket.SupportTicketResponse(
                id=ticket.id,
                title=ticket.title,
                description=ticket.description,
                category=ticket.category,
                status=ticket.status,
                priority=ticket.priority,
                user_id=ticket.user_id,
                admin_response=ticket.admin_response,
                assigned_to=ticket.assigned_to,
                created_at=ticket.created_at,
                updated_at=ticket.updated_at,
                resolved_at=ticket.resolved_at
            )
            for ticket in tickets
        ]
        
    except Exception as e:
        logger.error(f"Error fetching tickets for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching support tickets"
        )


@router.get("/tickets/{ticket_id}", response_model=schemas_support_ticket.SupportTicketResponse)
def get_ticket_by_id(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_broker_user)
):
    """
    Get a specific support ticket by ID.
    Only the ticket owner can access it.
    """
    try:
        ticket = crud_support_ticket.get_ticket_by_id(
            db=db,
            ticket_id=ticket_id,
            user_id=current_user.id
        )
        
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Support ticket not found or you don't have permission to access it"
            )
        
        return schemas_support_ticket.SupportTicketResponse(
            id=ticket.id,
            title=ticket.title,
            description=ticket.description,
            category=ticket.category,
            status=ticket.status,
            priority=ticket.priority,
            user_id=ticket.user_id,
            admin_response=ticket.admin_response,
            assigned_to=ticket.assigned_to,
            created_at=ticket.created_at,
            updated_at=ticket.updated_at,
            resolved_at=ticket.resolved_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching ticket {ticket_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the support ticket"
        )


# Admin endpoints
@router.get("/admin/tickets", response_model=List[schemas_support_ticket.SupportTicketResponse])
def get_all_tickets(
    status: Optional[str] = Query(None, description="Filter by status"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    category: Optional[str] = Query(None, description="Filter by category"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_insureflow_admin)
):
    """
    Get all support tickets (admin only).
    Admins can filter by status, priority, and category.
    """
    try:
        tickets = crud_support_ticket.get_all_tickets(
            db=db,
            status=status,
            priority=priority,
            category=category,
            skip=skip,
            limit=limit
        )
        
        return [
            schemas_support_ticket.SupportTicketResponse(
                id=ticket.id,
                title=ticket.title,
                description=ticket.description,
                category=ticket.category,
                status=ticket.status,
                priority=ticket.priority,
                user_id=ticket.user_id,
                admin_response=ticket.admin_response,
                assigned_to=ticket.assigned_to,
                created_at=ticket.created_at,
                updated_at=ticket.updated_at,
                resolved_at=ticket.resolved_at
            )
            for ticket in tickets
        ]
        
    except Exception as e:
        logger.error(f"Error fetching all tickets: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching support tickets"
        )


@router.get("/admin/tickets/{ticket_id}", response_model=schemas_support_ticket.SupportTicketResponse)
def get_admin_ticket_by_id(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_insureflow_admin)
):
    """
    Get a specific support ticket by ID (admin only).
    """
    try:
        ticket = crud_support_ticket.get_ticket_by_id(
            db=db,
            ticket_id=ticket_id
        )
        
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Support ticket not found"
            )
        
        return schemas_support_ticket.SupportTicketResponse(
            id=ticket.id,
            title=ticket.title,
            description=ticket.description,
            category=ticket.category,
            status=ticket.status,
            priority=ticket.priority,
            user_id=ticket.user_id,
            admin_response=ticket.admin_response,
            assigned_to=ticket.assigned_to,
            created_at=ticket.created_at,
            updated_at=ticket.updated_at,
            resolved_at=ticket.resolved_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching ticket {ticket_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the support ticket"
        )


@router.patch("/admin/tickets/{ticket_id}", response_model=schemas_support_ticket.SupportTicketResponse)
def update_ticket(
    ticket_id: int,
    ticket_update: schemas_support_ticket.SupportTicketUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_insureflow_admin)
):
    """
    Update a support ticket (admin only).
    Admins can update status, add admin response, and assign tickets.
    """
    try:
        # Get the ticket first
        ticket = crud_support_ticket.get_ticket_by_id(db=db, ticket_id=ticket_id)
        
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Support ticket not found"
            )
        
        # Update status if provided
        if ticket_update.status:
            ticket = crud_support_ticket.update_ticket_status(
                db=db,
                ticket_id=ticket_id,
                status=ticket_update.status,
                admin_id=current_user.id
            )
        
        # Add admin response if provided
        if ticket_update.admin_response:
            ticket = crud_support_ticket.add_admin_response(
                db=db,
                ticket_id=ticket_id,
                admin_response=ticket_update.admin_response,
                admin_id=current_user.id
            )
        
        # Refresh to get latest state
        db.refresh(ticket)
        
        return schemas_support_ticket.SupportTicketResponse(
            id=ticket.id,
            title=ticket.title,
            description=ticket.description,
            category=ticket.category,
            status=ticket.status,
            priority=ticket.priority,
            user_id=ticket.user_id,
            admin_response=ticket.admin_response,
            assigned_to=ticket.assigned_to,
            created_at=ticket.created_at,
            updated_at=ticket.updated_at,
            resolved_at=ticket.resolved_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating ticket {ticket_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the support ticket"
        )

