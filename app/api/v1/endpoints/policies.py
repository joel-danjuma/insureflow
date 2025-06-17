"""
API endpoints for policy management.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crud import policy as policy_crud
from app.dependencies import get_current_broker_or_admin_user
from app.models.user import User
from app.schemas.policy import Policy, PolicyCreate, PolicyUpdate

router = APIRouter()

@router.post("/", response_model=Policy, status_code=status.HTTP_201_CREATED)
def create_policy(
    policy: PolicyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_broker_or_admin_user)
):
    """
    Create a new policy. Broker or Admin only.
    """
    return policy_crud.create_policy(db=db, policy=policy)

@router.get("/", response_model=List[Policy])
def list_policies(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_broker_or_admin_user)
):
    """
    Retrieve a list of policies. Broker or Admin only.
    """
    policies = policy_crud.get_policies(db, skip=skip, limit=limit)
    return policies

@router.get("/{policy_id}", response_model=Policy)
def get_policy(
    policy_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_broker_or_admin_user)
):
    """
    Get a specific policy by ID. Broker or Admin only.
    """
    db_policy = policy_crud.get_policy(db, policy_id=policy_id)
    if db_policy is None:
        raise HTTPException(status_code=404, detail="Policy not found")
    return db_policy

@router.put("/{policy_id}", response_model=Policy)
def update_policy(
    policy_id: int,
    policy: PolicyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_broker_or_admin_user)
):
    """
    Update a policy. Broker or Admin only.
    """
    db_policy = policy_crud.update_policy(db, policy_id=policy_id, policy_update=policy)
    if db_policy is None:
        raise HTTPException(status_code=404, detail="Policy not found")
    return db_policy

@router.delete("/{policy_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_policy(
    policy_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_broker_or_admin_user)
):
    """
    Delete a policy. Broker or Admin only.
    """
    if not policy_crud.delete_policy(db, policy_id=policy_id):
        raise HTTPException(status_code=404, detail="Policy not found")
    return 