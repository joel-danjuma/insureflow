"""
CRUD operations for the User model.
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.auth import UserCreate
from app.schemas.user import UserUpdate
from app.core.security import get_password_hash

def get_user_by_email(db: Session, email: str) -> User:
    """
    Retrieves a user from the database by their email address.
    """
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: int) -> User:
    """
    Retrieves a user from the database by their ID.
    """
    return db.query(User).filter(User.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """
    Retrieves a list of users with pagination.
    """
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate) -> User:
    """
    Creates a new user in the database.
    """
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        role=user.role,
        is_active=True,  # Default to active on creation
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_update: UserUpdate) -> User:
    """
    Updates a user's information in the database.
    """
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
    
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int) -> bool:
    """
    Deletes a user from the database.
    Returns True if successful, False if user not found.
    """
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return False
    
    db.delete(db_user)
    db.commit()
    return True 