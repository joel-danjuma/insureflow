"""
API endpoints for premium management.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crud import premium as premium_crud
from app.dependencies import get_current_broker_or_admin_user
from app.models.user import User
from app.schemas.premium import Premium, PremiumCreate, PremiumUpdate
from app.schemas.payment import PaymentInitiationResponse
from app.services import payment_service

router = APIRouter()

@router.get("/", response_model=List[Premium])
def list_premiums(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_broker_or_admin_user)
):
    """
    Retrieve a list of premiums. Broker or Admin only.
    Brokers see only premiums for their policies. Admins see all premiums.
    """
    from app.models.user import UserRole
    
    # Check user role and filter premiums accordingly
    if current_user.role == UserRole.BROKER:
        if current_user.broker_profile:
            premiums = premium_crud.get_premiums_by_broker(
                db, broker_id=current_user.broker_profile.id, skip=skip, limit=limit
            )
        else:
            # If for some reason a broker user has no profile, return empty list
            premiums = []
    elif current_user.can_perform_admin_actions:
        # Admin can see all premiums
        premiums = premium_crud.get_premiums(db, skip=skip, limit=limit)
    else:
        # Fallback for unexpected roles
        premiums = []
    
    if not premiums:
        # Return empty list instead of mock data to prevent validation errors
        return []
    
    return premiums

@router.post("/", response_model=Premium, status_code=status.HTTP_201_CREATED)
def create_premium(
    premium: PremiumCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_broker_or_admin_user)
):
    """
    Create a new premium for a policy. Broker or Admin only.
    """
    return premium_crud.create_premium(db=db, premium=premium)

@router.get("/by-policy/{policy_id}", response_model=List[Premium])
def list_premiums_for_policy(
    policy_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_broker_or_admin_user)
):
    """
    Retrieve a list of premiums for a specific policy. Broker or Admin only.
    """
    premiums = premium_crud.get_premiums_by_policy(db, policy_id=policy_id, skip=skip, limit=limit)
    return premiums

@router.get("/{premium_id}", response_model=Premium)
def get_premium(
    premium_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_broker_or_admin_user)
):
    """
    Get a specific premium by ID. Broker or Admin only.
    """
    db_premium = premium_crud.get_premium(db, premium_id=premium_id)
    if db_premium is None:
        raise HTTPException(status_code=404, detail="Premium not found")
    return db_premium

@router.put("/{premium_id}", response_model=Premium)
def update_premium(
    premium_id: int,
    premium: PremiumUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_broker_or_admin_user)
):
    """
    Update a premium. Broker or Admin only.
    """
    db_premium = premium_crud.update_premium(db, premium_id=premium_id, premium_update=premium)
    if db_premium is None:
        raise HTTPException(status_code=404, detail="Premium not found")
    return db_premium

@router.delete("/{premium_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_premium(
    premium_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_broker_or_admin_user)
):
    """
    Delete a premium. Broker or Admin only.
    """
    if not premium_crud.delete_premium(db, premium_id=premium_id):
        raise HTTPException(status_code=404, detail="Premium not found")
    return 

@router.post("/{premium_id}/pay", response_model=PaymentInitiationResponse)
async def pay_for_premium(
    premium_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_broker_or_admin_user)
):
    """
    Initiate payment for a specific premium. Broker or Admin only.
    """
    return await payment_service.initiate_premium_payment(premium_id=premium_id, db=db) 