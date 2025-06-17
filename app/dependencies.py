"""
FastAPI dependencies for the application.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError

from app.core.database import get_db
from app.core.security import decode_access_token
from app.crud import user as user_crud
from app.models.user import User
from app.schemas.auth import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    Dependency to get the current user from a JWT token.
    --- FOR TESTING: THIS IS CURRENTLY BYPASSED TO RETURN THE FIRST USER ---
    """
    user = db.query(User).first()
    if user is None:
        # If no users exist, raise an error to indicate the app needs a user to be created.
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No users found in the database. Please register a user first.",
        )
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to get the current active user.
    --- FOR TESTING: THIS IS CURRENTLY BYPASSED ---
    """
    if not current_user: # Added check for None
        raise HTTPException(status_code=400, detail="No active user found for testing.")
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def get_current_admin_user(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Dependency to get the current user if they are an admin.
    Raises HTTP 403 if the user is not an admin.
    """
    if current_user.role != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

def get_current_broker_or_admin_user(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Dependency to get the current user if they are a broker or admin.
    Raises HTTP 403 if the user is neither a broker nor an admin.
    """
    if current_user.role not in ["Admin", "Broker"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user 