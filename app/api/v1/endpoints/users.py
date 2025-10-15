"""
API endpoints for user management.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import json
import secrets
import string
from redis.asyncio import Redis

from app import crud, schemas
from app.core.database import get_db
from app.core.cache import get_redis_client
from app.dependencies import get_current_admin_user, get_current_active_user, get_current_insurance_admin, get_current_broker_or_admin_user
from app.models.user import User, UserRole
from app.services.virtual_account_service import virtual_account_service


router = APIRouter()


@router.post("/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def create_user_public(
    *,
    db: Session = Depends(get_db),
    user_in: schemas.UserCreate,
):
    """
    Create new user. This is the public registration endpoint.
    """
    user = crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    user = crud.user.create(db, obj_in=user_in)
    return user


@router.get("/", response_model=List[schemas.User])
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Retrieve a list of users. Admin only.
    """
    users = crud.user.get_users(db, skip=skip, limit=limit)
    return users


@router.get("/me", response_model=schemas.User)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
    redis_client: Redis = Depends(get_redis_client)
):
    """
    Get current user's information.
    """
    cache_key = f"user:{current_user.id}"
    cached_user = await redis_client.get(cache_key)

    if cached_user:
        return json.loads(cached_user)

    user_data = schemas.User.model_validate(current_user).model_dump_json()
    await redis_client.set(cache_key, user_data, ex=300)  # Cache for 5 minutes
    
    return current_user


@router.get("/{user_id}", response_model=schemas.User)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get a specific user by ID. Admin only.
    """
    user = crud.user.get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.put("/{user_id}", response_model=schemas.User)
async def update_user(
    user_id: int,
    user_update: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
    redis_client: Redis = Depends(get_redis_client)
):
    """
    Update a user's information. Admin only.
    """
    db_user = crud.user.update_user(db, user_id=user_id, user_update=user_update)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    # Invalidate cache
    cache_key = f"user:{user_id}"
    await redis_client.delete(cache_key)
    return db_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
    redis_client: Redis = Depends(get_redis_client)
):
    """
    Delete a user. Admin only.
    """
    success = crud.user.delete_user(db, user_id=user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    # Invalidate cache
    cache_key = f"user:{user_id}"
    await redis_client.delete(cache_key)
    return None


def generate_strong_password(length: int = 12) -> str:
    """Generate a strong password with uppercase, lowercase, numbers, and symbols."""
    # Ensure we have at least one character from each category
    uppercase = string.ascii_uppercase
    lowercase = string.ascii_lowercase
    digits = string.digits
    symbols = "!@#$%^&*"
    
    # Start with one character from each category
    password = [
        secrets.choice(uppercase),
        secrets.choice(lowercase),
        secrets.choice(digits),
        secrets.choice(symbols)
    ]
    
    # Fill the rest with random characters from all categories
    all_chars = uppercase + lowercase + digits + symbols
    for _ in range(length - 4):
        password.append(secrets.choice(all_chars))
    
    # Shuffle the password to avoid predictable patterns
    secrets.SystemRandom().shuffle(password)
    return ''.join(password)


@router.post("/create-broker", response_model=schemas.BrokerUserCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_broker_user_with_virtual_account(
    *,
    db: Session = Depends(get_db),
    user_data: schemas.BrokerUserCreate,
    current_user: User = Depends(get_current_broker_or_admin_user)
):
    """
    Create a new broker user with auto-generated password and virtual account.
    Admin or Insurance Admin only.
    """
    # Check if user has permission to create broker users
    if not (current_user.role == UserRole.ADMIN or current_user.role == UserRole.INSURANCE_ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or Insurance Admin access required to create broker users"
        )
    
    try:
        # Check if user already exists
        existing_user = crud.user.get_user_by_email(db, email=user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="A user with this email already exists in the system."
            )
        
        # Check if username already exists
        existing_username = crud.user.get_user_by_username(db, username=user_data.username)
        if existing_username:
            raise HTTPException(
                status_code=400,
                detail="A user with this username already exists in the system."
            )
        
        # Generate strong password
        generated_password = generate_strong_password()
        
        # Create user data for CRUD
        user_create_data = schemas.UserCreate(
            email=user_data.email,
            full_name=user_data.full_name,
            password=generated_password,
            role=UserRole.BROKER.value
        )
        
        # Create the user
        new_user = crud.user.create_user(db, obj_in=user_create_data)
        
        # Update additional fields
        if user_data.username:
            new_user.username = user_data.username
        if user_data.phone_number:
            new_user.phone_number = user_data.phone_number
        if user_data.organization_name:
            new_user.organization_name = user_data.organization_name
        if user_data.bvn:
            new_user.bvn = user_data.bvn
        if user_data.date_of_birth:
            new_user.date_of_birth = user_data.date_of_birth
        if user_data.gender:
            new_user.gender = user_data.gender
        if user_data.address:
            new_user.address = user_data.address
        
        db.commit()
        db.refresh(new_user)
        
        # Create virtual account
        virtual_account_result = await virtual_account_service.create_individual_virtual_account(
            db=db,
            user=new_user
        )
        
        if virtual_account_result.get("error"):
            # User was created but virtual account failed
            return schemas.BrokerUserCreateResponse(
                success=True,
                user=new_user,
                generated_password=generated_password,
                virtual_account=None,
                message=f"User created successfully, but virtual account creation failed: {virtual_account_result['error']}"
            )
        
        # Success - both user and virtual account created
        virtual_account = virtual_account_result.get("virtual_account")
        virtual_account_data = {
            "id": virtual_account.id,
            "customer_identifier": virtual_account.customer_identifier,
            "virtual_account_number": virtual_account.virtual_account_number,
            "bank_code": virtual_account.bank_code,
            "account_type": virtual_account.account_type.value,
            "status": virtual_account.status.value,
        } if virtual_account else None
        
        return schemas.BrokerUserCreateResponse(
            success=True,
            user=new_user,
            generated_password=generated_password,
            virtual_account=virtual_account_data,
            message="Broker user and virtual account created successfully!"
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Handle unexpected errors
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        ) 