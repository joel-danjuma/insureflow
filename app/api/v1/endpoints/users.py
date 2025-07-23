"""
API endpoints for user management.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import json
from redis.asyncio import Redis

from app import crud, schemas
from app.core.database import get_db
from app.core.cache import get_redis_client
from app.dependencies import get_current_admin_user, get_current_active_user
from app.models.user import User


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