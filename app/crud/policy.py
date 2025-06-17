"""
CRUD operations for the Policy model.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.policy import Policy
from app.schemas.policy import PolicyCreate, PolicyUpdate

def get_policy(db: Session, policy_id: int) -> Optional[Policy]:
    """
    Retrieves a policy from the database by its ID.
    """
    return db.query(Policy).filter(Policy.id == policy_id).first()

def get_policies(db: Session, skip: int = 0, limit: int = 100) -> List[Policy]:
    """
    Retrieves a list of policies from the database.
    """
    return db.query(Policy).offset(skip).limit(limit).all()

def create_policy(db: Session, policy: PolicyCreate) -> Policy:
    """
    Creates a new policy in the database.
    """
    db_policy = Policy(**policy.model_dump())
    db.add(db_policy)
    db.commit()
    db.refresh(db_policy)
    return db_policy

def update_policy(db: Session, policy_id: int, policy_update: PolicyUpdate) -> Optional[Policy]:
    """
    Updates an existing policy in the database.
    """
    db_policy = get_policy(db, policy_id)
    if db_policy:
        update_data = policy_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_policy, key, value)
        db.add(db_policy)
        db.commit()
        db.refresh(db_policy)
    return db_policy

def delete_policy(db: Session, policy_id: int) -> bool:
    """
    Deletes a policy from the database.
    """
    db_policy = get_policy(db, policy_id)
    if db_policy:
        db.delete(db_policy)
        db.commit()
        return True
    return False 