"""
Pydantic schemas for support tickets.
"""
from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime


class SupportTicketCreate(BaseModel):
    """Schema for creating a support ticket."""
    title: str
    description: str
    category: str = "general"
    priority: str = "medium"
    
    @validator('title')
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError('Title is required and cannot be empty')
        if len(v) > 200:
            raise ValueError('Title must be less than 200 characters')
        return v.strip()
    
    @validator('description')
    def validate_description(cls, v):
        if not v or not v.strip():
            raise ValueError('Description is required and cannot be empty')
        return v.strip()
    
    @validator('category')
    def validate_category(cls, v):
        allowed_categories = ['general', 'policies', 'payments', 'commissions', 'technical']
        if v not in allowed_categories:
            raise ValueError(f'Category must be one of: {", ".join(allowed_categories)}')
        return v
    
    @validator('priority')
    def validate_priority(cls, v):
        allowed_priorities = ['low', 'medium', 'high']
        if v not in allowed_priorities:
            raise ValueError(f'Priority must be one of: {", ".join(allowed_priorities)}')
        return v


class SupportTicketUpdate(BaseModel):
    """Schema for updating a support ticket (admin only)."""
    status: Optional[str] = None
    admin_response: Optional[str] = None
    assigned_to: Optional[int] = None
    
    @validator('status')
    def validate_status(cls, v):
        if v is not None:
            allowed_statuses = ['open', 'in_progress', 'resolved', 'closed']
            if v not in allowed_statuses:
                raise ValueError(f'Status must be one of: {", ".join(allowed_statuses)}')
        return v
    
    @validator('admin_response')
    def validate_admin_response(cls, v):
        if v is not None and not v.strip():
            return None
        return v.strip() if v else None


class SupportTicketResponse(BaseModel):
    """Schema for support ticket response."""
    id: int
    title: str
    description: str
    category: str
    status: str
    priority: str
    user_id: int
    admin_response: Optional[str] = None
    assigned_to: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SupportTicketList(BaseModel):
    """Schema for list of support tickets."""
    tickets: list[SupportTicketResponse]
    total: int
    
    class Config:
        from_attributes = True

