"""
Dependencies for the InsureFlow application.
"""
from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from app.crud import user as crud_user
from app.models.user import User, UserRole
from app.schemas.auth import TokenData

# OAuth2 scheme for authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

def get_db() -> Generator:
    """
    Dependency to get database session.
    """
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def get_current_user(
    db: Session = Depends(get_db), 
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Get current authenticated user from JWT token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token, 
            settings.jwt_secret, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    user = crud_user.get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current active user (must be active and verified if required).
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Inactive user"
        )
    return current_user

def get_current_admin_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Get current user with admin privileges.
    """
    if not current_user.can_perform_admin_actions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user

def get_current_insureflow_admin(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Get current user with InsureFlow platform admin privileges.
    Only allows global ADMIN role access to internal platform data.
    Restricts access from insurance company and broker admins.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="InsureFlow platform admin privileges required. Only global administrators can access internal platform data."
        )
    return current_user

def get_current_broker_or_admin_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Get current user who is either a broker or admin.
    """
    allowed_roles = [
        UserRole.ADMIN,
        UserRole.BROKER,
        UserRole.BROKER_ADMIN,
        UserRole.BROKER_ACCOUNTANT,
        UserRole.INSURANCE_ADMIN,
        UserRole.INSURANCE_ACCOUNTANT
    ]
    
    if current_user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Broker or admin access required"
        )
    return current_user

def get_current_insurance_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Get current user who belongs to an insurance company.
    """
    if not current_user.is_insurance_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insurance company access required"
        )
    return current_user

def get_current_insurance_admin(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Get current user who is an insurance company admin.
    """
    if current_user.role != UserRole.INSURANCE_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insurance company administrator access required"
        )
    return current_user

def get_current_policy_creator(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Get current user who can create policies (Insurance Admin or Accountant with permission).
    """
    if not (current_user.is_insurance_user and 
            (current_user.can_perform_admin_actions or current_user.can_create_policies)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Policy creation access required. Must be Insurance Admin or Accountant with policy creation permission."
        )
    return current_user

def get_current_payment_processor(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Get current user who can process payments (Broker Admin or Accountant with permission).
    """
    if not (current_user.is_broker_user and 
            (current_user.can_perform_admin_actions or current_user.can_make_payments)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Payment processing access required. Must be Broker Admin or Accountant with payment permission."
        )
    return current_user

def get_current_broker_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Get current user who is a broker.
    """
    if not current_user.is_broker_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Broker access required"
        )
    return current_user

def require_verified_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Require user to be verified for sensitive operations.
    """
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account verification required for this operation"
        )
    return current_user 

def get_user_with_role(required_role: UserRole):
    """
    Factory function to create a dependency that requires a specific role.
    """
    def role_dependency(
        current_user: User = Depends(get_current_active_user),
    ) -> User:
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role {required_role.value} required"
            )
        return current_user
    
    return role_dependency

def get_user_with_any_role(allowed_roles: list[UserRole]):
    """
    Factory function to create a dependency that requires any of the specified roles.
    """
    def role_dependency(
        current_user: User = Depends(get_current_active_user),
    ) -> User:
        if current_user.role not in allowed_roles:
            role_names = [role.value for role in allowed_roles]
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"One of these roles required: {', '.join(role_names)}"
            )
        return current_user
    
    return role_dependency

def get_current_insureflow_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current user and verify they have InsureFlow admin role.
    Only InsureFlow admins can access settlement management.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Only InsureFlow platform admins can access this resource"
        )
    return current_user 