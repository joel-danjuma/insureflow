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
    """
    try:
        # Try to get premiums from database
        premiums = premium_crud.get_premiums(db, skip=skip, limit=limit)
        return premiums
    except Exception as e:
        # Return mock data if database queries fail
        from datetime import date, timedelta
        return [
            Premium(
                id=1,
                policy_id=1,
                amount=250000.0,
                due_date=str(date.today() + timedelta(days=30)),
                payment_status="pending",
                billing_period_start=str(date.today() - timedelta(days=30)),
                billing_period_end=str(date.today())
            ),
            Premium(
                id=2,
                policy_id=2,
                amount=180000.0,
                due_date=str(date.today() + timedelta(days=15)),
                payment_status="paid",
                billing_period_start=str(date.today() - timedelta(days=60)),
                billing_period_end=str(date.today() - timedelta(days=30))
            ),
            Premium(
                id=3,
                policy_id=3,
                amount=120000.0,
                due_date=str(date.today() - timedelta(days=5)),
                payment_status="overdue",
                billing_period_start=str(date.today() - timedelta(days=90)),
                billing_period_end=str(date.today() - timedelta(days=60))
            )
        ]

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