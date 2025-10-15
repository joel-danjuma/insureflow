"""
API endpoints for user authentication and management.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List

from app import dependencies
from app.core.security import create_access_token, verify_password, get_password_hash
from app.crud import user as crud_user, broker as crud_broker
from app.schemas.auth import (
    UserCreate, Token, UserResponse, UserUpdate, PasswordUpdate,
    BrokerOnboardingRequest, UserInvitation, UserRolePermissions
)
from app.core.config import settings
from app.models.user import User, UserRole

router = APIRouter()

@router.post("/register", response_model=Token)
def register_user(
    *,
    db: Session = Depends(dependencies.get_db),
    user_in: UserCreate,
):
    """
    Create new user account and return an access token.
    Enhanced with additional user fields and role validation.
    """
    # Check if user already exists
    user = crud_user.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists.",
        )
    
    # Check if username is taken
    existing_user = crud_user.get_user_by_username(db, username=user_in.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken.",
        )
    
    # Create new user
    new_user = crud_user.create_user(db, user=user_in)
    
    # Automatically log in the user after registration
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": new_user.email}, expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.from_orm(new_user)
    )

@router.post("/login", response_model=Token)
def login_for_access_token(
    db: Session = Depends(dependencies.get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = crud_user.authenticate_user(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is deactivated"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    # Update last login time
    crud_user.update_last_login(db, user_id=user.id)
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.from_orm(user)
    ) 

@router.get("/me", response_model=UserResponse)
def read_user_me(
    current_user: User = Depends(dependencies.get_current_active_user),
):
    """
    Get current user information.
    """
    return current_user

@router.put("/me", response_model=UserResponse)
def update_user_me(
    *,
    db: Session = Depends(dependencies.get_db),
    user_update: UserUpdate,
    current_user: User = Depends(dependencies.get_current_active_user),
):
    """
    Update current user information.
    """
    # Only allow non-admin fields for regular users
    if not current_user.can_perform_admin_actions:
        # Remove admin-only fields
        user_update.is_active = None
        user_update.is_verified = None
        user_update.can_create_policies = None
        user_update.can_make_payments = None
        user_update.role = None
    
    updated_user = crud_user.update_user(db, user_id=current_user.id, user_update=user_update)
    return updated_user

@router.put("/me/password")
def update_password(
    *,
    db: Session = Depends(dependencies.get_db),
    password_update: PasswordUpdate,
    current_user: User = Depends(dependencies.get_current_active_user),
):
    """
    Update current user password.
    """
    # Verify current password
    if not verify_password(password_update.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    # Update password
    hashed_password = get_password_hash(password_update.new_password)
    crud_user.update_user_password(db, user_id=current_user.id, hashed_password=hashed_password)
    
    return {"message": "Password updated successfully"}

@router.post("/onboard-broker", response_model=UserResponse)
def onboard_broker(
    *,
    db: Session = Depends(dependencies.get_db),
    broker_request: BrokerOnboardingRequest,
    current_user: User = Depends(dependencies.get_current_active_user),
):
    """
    Onboard a new broker (Insurance company admin only).
    """
    # Check if current user is an insurance admin
    if not current_user.is_insurance_user or not current_user.can_perform_admin_actions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only insurance company administrators can onboard brokers"
        )
    
    # Check if user already exists
    existing_user = crud_user.get_user_by_email(db, email=broker_request.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Create broker user account
    # Generate a temporary username if not provided
    username = broker_request.email.split('@')[0]
    counter = 1
    original_username = username
    while crud_user.get_user_by_username(db, username=username):
        username = f"{original_username}_{counter}"
        counter += 1
    
    # Create user with broker role
    user_data = UserCreate(
        username=username,
        email=broker_request.email,
        password="TempPassword123!",  # They'll need to change this on first login
        full_name=broker_request.full_name,
        role=broker_request.role,
        phone_number=broker_request.phone_number,
        organization_name=broker_request.organization_name,
        can_make_payments=broker_request.can_make_payments if broker_request.role == "BROKER_ACCOUNTANT" else False
    )
    
    new_broker = crud_user.create_user(db, user=user_data)

    # Create the broker profile
    broker_profile_data = {
        "name": new_broker.full_name,
        "agency_name": new_broker.organization_name,
        # Add any other broker-specific fields here
    }
    crud_broker.create_broker_profile(db, user_id=new_broker.id, broker_data=broker_profile_data)

    # TODO: Send invitation email with temporary password
    # email_service.send_broker_invitation(new_broker.email, "TempPassword123!")

    return new_broker

@router.get("/users", response_model=List[UserResponse])
def list_users(
    skip: int = 0,
    limit: int = 100,
    role: str = None,
    db: Session = Depends(dependencies.get_db),
    current_user: User = Depends(dependencies.get_current_active_user),
):
    """
    List users (admin only).
    """
    if not current_user.can_perform_admin_actions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    users = crud_user.get_users(db, skip=skip, limit=limit, role=role)
    return users

@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(dependencies.get_db),
    current_user: User = Depends(dependencies.get_current_active_user),
):
    """
    Get user by ID (admin only).
    """
    if not current_user.can_perform_admin_actions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    user = crud_user.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(dependencies.get_db),
    current_user: User = Depends(dependencies.get_current_active_user),
):
    """
    Update user (admin only).
    """
    if not current_user.can_perform_admin_actions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    user = crud_user.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    updated_user = crud_user.update_user(db, user_id=user_id, user_update=user_update)
    return updated_user

@router.put("/users/{user_id}/permissions", response_model=UserResponse)
def update_user_permissions(
    user_id: int,
    permissions: UserRolePermissions,
    db: Session = Depends(dependencies.get_db),
    current_user: User = Depends(dependencies.get_current_active_user),
):
    """
    Update user role and permissions (admin only).
    """
    if not current_user.can_perform_admin_actions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    user = crud_user.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update user permissions
    user_update = UserUpdate(
        role=permissions.role,
        can_create_policies=permissions.can_create_policies,
        can_make_payments=permissions.can_make_payments
    )
    
    updated_user = crud_user.update_user(db, user_id=user_id, user_update=user_update)
    return updated_user

@router.delete("/users/{user_id}")
def deactivate_user(
    user_id: int,
    db: Session = Depends(dependencies.get_db),
    current_user: User = Depends(dependencies.get_current_active_user),
):
    """
    Deactivate user (admin only).
    """
    if not current_user.can_perform_admin_actions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    user = crud_user.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )
    
    # Soft delete by deactivating
    user_update = UserUpdate(is_active=False)
    crud_user.update_user(db, user_id=user_id, user_update=user_update)
    
    return {"message": "User deactivated successfully"}

@router.get("/roles")
def get_available_roles(
    current_user: User = Depends(dependencies.get_current_active_user),
):
    """
    Get available user roles.
    """
    if current_user.can_perform_admin_actions:
        # Admin can see all roles
        return [
            {"value": "ADMIN", "label": "System Administrator"},
            {"value": "INSURANCE_ADMIN", "label": "Insurance Company Administrator"},
            {"value": "INSURANCE_ACCOUNTANT", "label": "Insurance Company Accountant"},
            {"value": "BROKER_ADMIN", "label": "Broker Administrator"},
            {"value": "BROKER_ACCOUNTANT", "label": "Broker Accountant"},
            {"value": "BROKER", "label": "Broker"},
            {"value": "CUSTOMER", "label": "Customer"},
        ]
    elif current_user.is_insurance_user:
        # Insurance users can only create broker roles
        return [
            {"value": "BROKER_ADMIN", "label": "Broker Administrator"},
            {"value": "BROKER_ACCOUNTANT", "label": "Broker Accountant"},
            {"value": "BROKER", "label": "Broker"},
        ]
    else:
        # Regular users can't create accounts
        return [] 