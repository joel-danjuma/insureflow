"""
Pydantic schemas for policy-related operations.
"""
from datetime import date
from pydantic import BaseModel
from typing import Optional

class PolicyBase(BaseModel):
    policy_number: str
    start_date: date
    end_date: date
    status: str = "pending"
    company_id: int
    broker_id: Optional[int] = None
    customer_id: int

class PolicyCreate(PolicyBase):
    pass

class PolicyUpdate(BaseModel):
    policy_number: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = None

class Policy(PolicyBase):
    id: int

    class Config:
        from_attributes = True 