"""
CRUD operations for the Premium model.
"""
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.models.premium import Premium, PaymentStatus
from app.models.policy import Policy
from app.schemas.premium import PremiumCreate, PremiumUpdate


def get_premium(db: Session, premium_id: int) -> Optional[Premium]:
    """
    Retrieves a premium from the database by its ID with policy and user data.
    """
    return db.query(Premium).options(
        joinedload(Premium.policy).joinedload(Policy.user)
    ).filter(Premium.id == premium_id).first()

def get_premiums(db: Session, skip: int = 0, limit: int = 100) -> List[Premium]:
    """
    Retrieves a list of all premiums from the database with policy and user data.
    """
    return db.query(Premium).options(
        joinedload(Premium.policy).joinedload(Policy.user)
    ).offset(skip).limit(limit).all()

def get_premiums_by_policy(db: Session, policy_id: int, skip: int = 0, limit: int = 100) -> List[Premium]:
    """
    Retrieves a list of premiums for a specific policy from the database with policy and user data.
    """
    return db.query(Premium).options(
        joinedload(Premium.policy).joinedload(Policy.user)
    ).filter(Premium.policy_id == policy_id).offset(skip).limit(limit).all()

def get_premiums_by_broker(db: Session, broker_id: int, skip: int = 0, limit: int = 100) -> List[Premium]:
    """
    Retrieves a list of premiums for policies belonging to a specific broker with policy and user data.
    """
    return db.query(Premium).options(
        joinedload(Premium.policy).joinedload(Policy.user)
    ).join(Policy).filter(
        Policy.broker_id == broker_id
    ).offset(skip).limit(limit).all()

def get_unpaid_premiums_by_policy(db: Session, policy_id: int) -> List[Premium]:
    """
    Retrieves all unpaid premiums for a single policy with policy and user data.
    """
    return db.query(Premium).options(
        joinedload(Premium.policy).joinedload(Policy.user)
    ).filter(
        Premium.policy_id == policy_id,
        Premium.payment_status != PaymentStatus.PAID
    ).all()

def get_premiums_by_ids(db: Session, premium_ids: List[int]) -> List[Premium]:
    """
    Retrieves a list of premiums by their IDs.
    """
    return db.query(Premium).filter(Premium.id.in_(premium_ids)).all()

def get_unpaid_premiums_for_policies(db: Session, policy_ids: List[int]) -> List[Premium]:
    """
    Retrieves all unpaid premiums for a given list of policy IDs.
    """
    return db.query(Premium).filter(
        Premium.policy_id.in_(policy_ids),
        Premium.payment_status != PaymentStatus.PAID
    ).all()

def create_premium(db: Session, premium: PremiumCreate) -> Premium:
    """
    Creates a new premium in the database.
    """
    db_premium = Premium(**premium.model_dump())
    db.add(db_premium)
    db.commit()
    db.refresh(db_premium)
    return db_premium

def update_premium(db: Session, premium_id: int, premium_update: PremiumUpdate) -> Optional[Premium]:
    """
    Updates an existing premium in the database.
    """
    db_premium = get_premium(db, premium_id)
    if db_premium:
        update_data = premium_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_premium, key, value)
        db.add(db_premium)
        db.commit()
        db.refresh(db_premium)
    return db_premium

def delete_premium(db: Session, premium_id: int) -> bool:
    """
    Deletes a premium from the database.
    """
    db_premium = get_premium(db, premium_id)
    if db_premium:
        db.delete(db_premium)
        db.commit()
        return True
    return False

def update_premium_status_to_paid(db: Session, premium_id: int) -> Premium | None:
    """
    Updates the status of a premium to 'paid'.
    """
    premium = db.query(Premium).filter(Premium.id == premium_id).first()
    if premium:
        premium.payment_status = PaymentStatus.PAID
        db.add(premium)
        db.commit()
        db.refresh(premium)
    return premium 