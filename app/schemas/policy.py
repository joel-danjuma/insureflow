"""
Pydantic schemas for policy-related operations.
"""
from datetime import date
from decimal import Decimal
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any

class PolicyholderInfo(BaseModel):
    """Embedded schema for policyholder information."""
    company_name: str
    contact_person: str
    contact_email: EmailStr
    contact_phone: Optional[str] = None
    rc_number: Optional[str] = None

class CoverageDetails(BaseModel):
    """Embedded schema for coverage information."""
    coverage_amount: Decimal
    coverage_items: Optional[List[str]] = None
    beneficiaries: Optional[List[Dict[str, Any]]] = None
    coverage_description: Optional[str] = None

class CustomPaymentSchedule(BaseModel):
    """Schema for custom payment schedule entries."""
    payment_date: date
    amount: Decimal

class PolicyBase(BaseModel):
    # Policy Information
    policy_name: str
    policy_number: str
    policy_type: str
    start_date: date
    due_date: date
    end_date: date
    duration_months: Optional[int] = None
    
    # Payment & Premium Details
    premium_amount: Decimal
    payment_frequency: str = "monthly"
    first_payment_date: Optional[date] = None
    last_payment_date: Optional[date] = None
    grace_period_days: int = 30
    custom_payment_schedule: Optional[List[CustomPaymentSchedule]] = None
    
    # Policyholder Information
    company_name: str
    contact_person: str
    contact_email: EmailStr
    contact_phone: Optional[str] = None
    rc_number: Optional[str] = None
    
    # Coverage Details
    coverage_amount: Decimal
    coverage_items: Optional[List[str]] = None
    beneficiaries: Optional[List[Dict[str, Any]]] = None
    coverage_details: Optional[str] = None
    
    # Broker Visibility & Tags
    broker_id: Optional[int] = None
    broker_notes: Optional[str] = None
    internal_tags: Optional[List[str]] = None
    
    # Advanced Settings
    auto_renew: bool = False
    notify_broker_on_change: bool = True
    commission_structure: Optional[Dict[str, Any]] = None
    
    # Status and relationships
    status: str = "pending"
    company_id: int
    user_id: int

class PolicyCreate(PolicyBase):
    """Schema for creating a new policy."""
    pass

class PolicyUpdate(BaseModel):
    """Schema for updating an existing policy."""
    policy_name: Optional[str] = None
    policy_type: Optional[str] = None
    start_date: Optional[date] = None
    due_date: Optional[date] = None
    end_date: Optional[date] = None
    duration_months: Optional[int] = None
    
    premium_amount: Optional[Decimal] = None
    payment_frequency: Optional[str] = None
    first_payment_date: Optional[date] = None
    last_payment_date: Optional[date] = None
    grace_period_days: Optional[int] = None
    
    company_name: Optional[str] = None
    contact_person: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    rc_number: Optional[str] = None
    
    coverage_amount: Optional[Decimal] = None
    coverage_items: Optional[List[str]] = None
    beneficiaries: Optional[List[Dict[str, Any]]] = None
    coverage_details: Optional[str] = None
    
    broker_id: Optional[int] = None
    broker_notes: Optional[str] = None
    internal_tags: Optional[List[str]] = None
    
    auto_renew: Optional[bool] = None
    notify_broker_on_change: Optional[bool] = None
    
    status: Optional[str] = None

class Policy(PolicyBase):
    """Schema for policy responses."""
    id: int
    policy_number: str
    created_at: Optional[date] = None
    updated_at: Optional[date] = None

    class Config:
        from_attributes = True

class CustomerInfo(BaseModel):
    """Customer information for policy listings."""
    full_name: str
    email: str
    phone_number: Optional[str] = None

class PolicySummary(BaseModel):
    """Simplified schema for policy listings."""
    id: int
    policy_name: str
    policy_number: str
    policy_type: str
    company_name: str
    premium_amount: Decimal
    due_date: date
    payment_frequency: str
    status: str
    customer: Optional[CustomerInfo] = None

    class Config:
        from_attributes = True 