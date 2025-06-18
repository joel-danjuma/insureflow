"""
Pydantic schemas for user management.
"""
from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

from app.models.user import UserRole


# Shared properties
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str


# Properties to receive via API on update
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None


# Properties shared by models in DB
class UserInDBBase(UserBase):
    id: int
    is_active: bool
    role: str

    class Config:
        from_attributes = True


# Properties to return to client
class User(UserInDBBase):
    """
    User schema for responses (excludes sensitive data like hashed_password).
    """
    created_at: datetime
    updated_at: Optional[datetime] = None


# Properties stored in DB
class UserInDB(UserInDBBase):
    """
    Schema representing a user in the database (includes hashed_password).
    This should not be used for API responses.
    """
    hashed_password: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True 