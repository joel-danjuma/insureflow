"""
Pydantic schemas for user management.
"""
from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: str
    is_active: bool = True

class User(UserBase):
    """
    User schema for responses (excludes sensitive data like hashed_password).
    """
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    """
    Schema for updating user information.
    """
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None

class UserInDB(UserBase):
    """
    Schema representing a user in the database (includes hashed_password).
    This should not be used for API responses.
    """
    id: int
    hashed_password: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True 