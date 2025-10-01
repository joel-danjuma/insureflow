"""
API endpoints for insurance firm management.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import dependencies, models
from app.schemas.user import UserResponse

router = APIRouter()

@router.get("/me", response_model=UserResponse)
def read_insurance_me(
    current_user: models.user.User = Depends(dependencies.get_current_active_user),
    db: Session = Depends(dependencies.get_db)
):
    """
    Get current insurance firm user profile.
    Only accessible by INSURANCE_ADMIN and INSURANCE_ACCOUNTANT users.
    """
    if current_user.role not in [
        models.user.UserRole.INSURANCE_ADMIN, 
        models.user.UserRole.INSURANCE_ACCOUNTANT
    ]:
        raise HTTPException(status_code=403, detail="Not an insurance firm user")
    
    # Return the user profile for insurance firm users
    return current_user

@router.put("/me", response_model=UserResponse)
def update_insurance_me(
    user_update: dict,
    current_user: models.user.User = Depends(dependencies.get_current_active_user),
    db: Session = Depends(dependencies.get_db)
):
    """
    Update current insurance firm user profile.
    """
    if current_user.role not in [
        models.user.UserRole.INSURANCE_ADMIN, 
        models.user.UserRole.INSURANCE_ACCOUNTANT
    ]:
        raise HTTPException(status_code=403, detail="Not an insurance firm user")
    
    # For now, return current user (implement update logic later)
    return current_user


