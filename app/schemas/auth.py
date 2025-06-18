"""
Pydantic schemas for authentication.
"""
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str
    role: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    email: str
    role: str

class TokenData(BaseModel):
    email: EmailStr = None 