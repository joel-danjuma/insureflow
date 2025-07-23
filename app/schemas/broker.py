from pydantic import BaseModel, EmailStr
from typing import Optional

class BrokerBase(BaseModel):
    name: str
    license_number: str
    agency_name: Optional[str] = None
    contact_email: EmailStr
    contact_phone: Optional[str] = None
    office_address: Optional[str] = None

class BrokerCreate(BrokerBase):
    user_id: int

class BrokerUpdate(BaseModel):
    name: Optional[str] = None
    agency_name: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    office_address: Optional[str] = None

class Broker(BrokerBase):
    id: int
    user_id: int
    is_active: bool

    class Config:
        from_attributes = True 