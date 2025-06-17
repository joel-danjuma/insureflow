"""
Pydantic schemas for premium-related operations.
"""
from datetime import date
from pydantic import BaseModel
from typing import Optional

class PremiumBase(BaseModel):
    amount: float
    due_date: date
    status: str = "pending"
    policy_id: int

class PremiumCreate(PremiumBase):
    pass

class PremiumUpdate(BaseModel):
    amount: Optional[float] = None
    due_date: Optional[date] = None
    status: Optional[str] = None

class Premium(PremiumBase):
    id: int

    class Config:
        from_attributes = True 