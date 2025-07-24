"""
Pydantic schemas for authentication.
"""
from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str
    role: str
    
    # Enhanced registration fields
    phone_number: Optional[str] = None
    organization_name: Optional[str] = None  # Company/Organization name
    bvn: Optional[str] = None  # Bank Verification Number
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None  # "male", "female", "other"
    address: Optional[str] = None
    
    @validator('role')
    def validate_role(cls, v):
        allowed_roles = [
            'ADMIN', 'BROKER', 'CUSTOMER', 
            'INSURANCE_ADMIN', 'INSURANCE_ACCOUNTANT',
            'BROKER_ADMIN', 'BROKER_ACCOUNTANT'
        ]
        if v not in allowed_roles:
            raise ValueError(f'Role must be one of: {", ".join(allowed_roles)}')
        return v
    
    @validator('bvn')
    def validate_bvn(cls, v):
        if v and len(v) != 11:
            raise ValueError('BVN must be exactly 11 digits')
        if v and not v.isdigit():
            raise ValueError('BVN must contain only digits')
        return v
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        if v:
            # Remove any non-digit characters for validation
            digits_only = ''.join(filter(str.isdigit, v))
            if len(digits_only) < 10:
                raise ValueError('Phone number must have at least 10 digits')
        return v

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    username: str
    role: str
    
    # Enhanced user information
    phone_number: Optional[str] = None
    organization_name: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    
    # Status fields
    is_active: bool
    is_verified: bool
    can_create_policies: bool
    can_make_payments: bool
    
    # Role-based properties
    is_insurance_user: bool = False
    is_broker_user: bool = False
    can_perform_admin_actions: bool = False
    
    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

    @validator('role', pre=True, always=True)
    def normalize_role(cls, v):
        if isinstance(v, str):
            return v.lower()
        if hasattr(v, 'value'):
            return v.value.lower()
        return v

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    """Schema for updating user information."""
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    organization_name: Optional[str] = None
    address: Optional[str] = None
    
    # Admin-only fields
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    can_create_policies: Optional[bool] = None
    can_make_payments: Optional[bool] = None
    role: Optional[str] = None
    
    @validator('role')
    def validate_role(cls, v):
        if v:
            allowed_roles = [
                'ADMIN', 'BROKER', 'CUSTOMER', 
                'INSURANCE_ADMIN', 'INSURANCE_ACCOUNTANT',
                'BROKER_ADMIN', 'BROKER_ACCOUNTANT'
            ]
            if v not in allowed_roles:
                raise ValueError(f'Role must be one of: {", ".join(allowed_roles)}')
        return v

class PasswordUpdate(BaseModel):
    """Schema for updating user password."""
    current_password: str
    new_password: str
    confirm_password: str
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class TokenData(BaseModel):
    email: EmailStr = None 

class UserRolePermissions(BaseModel):
    """Schema for user role and permissions."""
    role: str
    can_create_policies: bool
    can_make_payments: bool
    can_perform_admin_actions: bool
    is_insurance_user: bool
    is_broker_user: bool

class BrokerOnboardingRequest(BaseModel):
    """Schema for broker onboarding by insurance company."""
    email: EmailStr
    full_name: str
    phone_number: str
    organization_name: Optional[str] = None
    role: str = "BROKER"  # Can be BROKER, BROKER_ADMIN, or BROKER_ACCOUNTANT
    
    # Permissions for accountant role
    can_make_payments: bool = False
    
    @validator('role')
    def validate_broker_role(cls, v):
        allowed_roles = ['BROKER', 'BROKER_ADMIN', 'BROKER_ACCOUNTANT']
        if v not in allowed_roles:
            raise ValueError(f'Role must be one of: {", ".join(allowed_roles)}')
        return v

class UserInvitation(BaseModel):
    """Schema for user invitation response."""
    id: int
    email: str
    full_name: str
    role: str
    organization_name: Optional[str] = None
    invited_by: str  # Email of user who sent invitation
    invitation_sent_at: datetime
    is_accepted: bool = False
    
    class Config:
        from_attributes = True 