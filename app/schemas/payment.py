"""
Pydantic schemas for payment-related operations.
"""
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from decimal import Decimal

from app.models.payment import PaymentMethod, PaymentTransactionStatus

class PaymentBase(BaseModel):
    premium_id: int
    amount_paid: Decimal
    currency: str = "NGN"
    payment_method: PaymentMethod
    status: PaymentTransactionStatus = PaymentTransactionStatus.PENDING
    transaction_reference: str
    payer_email: Optional[EmailStr] = None

class PaymentCreate(PaymentBase):
    pass

class PaymentUpdate(BaseModel):
    status: Optional[PaymentTransactionStatus] = None
    gateway_response: Optional[str] = None

class Payment(PaymentBase):
    id: int
    payment_date: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PaymentInitiationResponse(BaseModel):
    """
    Schema for the response after initiating a payment.
    """
    payment_url: str
    transaction_ref: str
    message: str

class SquadCoTransactionData(BaseModel):
    """
    Detailed schema for the transaction data within the SquadCo webhook payload.
    Using aliases to map from the API's naming convention.
    """
    transaction_reference: str = Field(..., alias="Transaction_Reference")
    status: str = Field(..., alias="Status")
    amount: float = Field(..., alias="Amount")
    merchant_amount: float = Field(..., alias="Merchant_Amount")
    fee: float = Field(..., alias="Fee")
    merchant_ref: Optional[str] = Field(None, alias="Merchant_ref")
    email: EmailStr = Field(..., alias="Email")
    created_at: datetime = Field(..., alias="Created_At")
    transaction_date: str = Field(..., alias="transaction_date")
    transaction_time: str = Field(..., alias="transaction_time")
    
    class Config:
        populate_by_name = True
        
class SquadCoWebhookPayload(BaseModel):
    """
    Schema for the entire Squad Co webhook payload.
    """
    event: str = Field(..., alias="Event")
    data: SquadCoTransactionData

    class Config:
        populate_by_name = True

class SquadCoWebhookData(BaseModel):
    """
    Schema for the data field in the SquadCo webhook payload.
    """
    Transaction_Reference: str
    Status: str
    Amount: float
    Merchant_Amount: float
    Fee: float
    Merchant_ref: str
    Email: str
    Created_At: str
    transaction_date: str
    transaction_time: str
    # Add other relevant fields from the webhook payload as needed 