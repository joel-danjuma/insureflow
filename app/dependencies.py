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
from app.models.user import User, UserRole
from app.schemas.auth import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    Dependency to get the current user from a JWT token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception
    token_data = TokenData(email=email)
    
    user = user_crud.get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to get the current active user.
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def get_current_admin_user(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Dependency to get the current user if they are an admin.
    Raises HTTP 403 if the user is not an admin.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Not enough permissions. User role: {current_user.role.value}, Required: admin"
        )
    return current_user

def get_current_broker_or_admin_user(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Dependency to get the current user if they are a broker or admin.
    Raises HTTP 403 if the user is neither a broker nor an admin.
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.BROKER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Not enough permissions. User role: {current_user.role.value}, Required: admin or broker"
        )
    return current_user

def get_current_broker_user(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Dependency to get the current user if they are a broker.
    Raises HTTP 403 if the user is not a broker.
    """
    if current_user.role != UserRole.BROKER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Not enough permissions. User role: {current_user.role.value}, Required: broker"
        )
    return current_user 