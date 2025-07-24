"""
Pydantic schemas for virtual account operations.
"""
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, EmailStr
from typing import Optional, List

class VirtualAccountBase(BaseModel):
    """Base schema for virtual account."""
    account_type: str
    mobile_number: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    platform_commission_rate: Decimal = Decimal('0.01')  # 1% total platform commission
    insureflow_commission_rate: Decimal = Decimal('0.0075')  # 0.75% to InsureFlow
    habari_commission_rate: Decimal = Decimal('0.0025')  # 0.25% to Habari
    auto_settlement: bool = True
    settlement_threshold: Decimal = Decimal('1000')

class IndividualVirtualAccountCreate(VirtualAccountBase):
    """Schema for creating individual virtual account."""
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    bvn: Optional[str] = None
    date_of_birth: Optional[str] = None  # DD/MM/YYYY format
    gender: Optional[str] = None  # "1" for male, "2" for female
    customer_identifier: Optional[str] = None

class BusinessVirtualAccountCreate(VirtualAccountBase):
    """Schema for creating business virtual account."""
    business_name: str
    bvn: Optional[str] = None
    customer_identifier: Optional[str] = None

class VirtualAccountUpdate(BaseModel):
    """Schema for updating virtual account."""
    status: Optional[str] = None
    platform_commission_rate: Optional[Decimal] = None
    insureflow_commission_rate: Optional[Decimal] = None
    habari_commission_rate: Optional[Decimal] = None
    auto_settlement: Optional[bool] = None
    settlement_threshold: Optional[Decimal] = None
    mobile_number: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None

class VirtualAccount(BaseModel):
    """Schema for virtual account response."""
    id: int
    user_id: int
    customer_identifier: str
    virtual_account_number: str
    bank_code: str
    account_type: str
    status: str
    
    # Account details based on type
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    business_name: Optional[str] = None
    
    # Contact information
    mobile_number: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    
    # Financial information
    total_credits: Decimal
    total_debits: Decimal
    current_balance: Decimal
    net_amount_after_commission: Decimal
    habari_commission_amount: Decimal
    insureflow_commission_amount: Decimal
    total_platform_commission: Decimal
    
    # Configuration
    platform_commission_rate: Decimal
    insureflow_commission_rate: Decimal
    habari_commission_rate: Decimal
    auto_settlement: bool
    settlement_threshold: Decimal
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    last_activity_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class VirtualAccountSummary(BaseModel):
    """Simplified schema for virtual account listings."""
    id: int
    customer_identifier: str
    virtual_account_number: str
    account_type: str
    display_name: str
    current_balance: Decimal
    status: str
    
    class Config:
        from_attributes = True

class VirtualAccountTransactionBase(BaseModel):
    """Base schema for virtual account transaction."""
    transaction_reference: str
    transaction_type: str
    principal_amount: Decimal
    currency: str = "NGN"
    remarks: Optional[str] = None

class VirtualAccountTransactionCreate(VirtualAccountTransactionBase):
    """Schema for creating virtual account transaction."""
    virtual_account_id: int
    transaction_indicator: str
    settled_amount: Optional[Decimal] = None
    fee_charged: Optional[Decimal] = Decimal('0')
    sender_name: Optional[str] = None
    policy_id: Optional[int] = None
    premium_id: Optional[int] = None

class VirtualAccountTransaction(BaseModel):
    """Schema for virtual account transaction response."""
    id: int
    virtual_account_id: int
    transaction_reference: str
    squad_transaction_reference: Optional[str] = None
    transaction_type: str
    transaction_indicator: str
    status: str
    
    # Financial details
    principal_amount: Decimal
    settled_amount: Decimal
    fee_charged: Decimal
    total_platform_commission: Decimal
    insureflow_commission: Decimal
    habari_commission: Decimal
    net_amount_to_user: Decimal
    
    # Transaction context
    currency: str
    channel: str
    sender_name: Optional[str] = None
    remarks: Optional[str] = None
    
    # Processing information
    transaction_date: datetime
    merchant_settlement_date: Optional[datetime] = None
    alerted_merchant: bool
    frozen_transaction: bool
    
    # Related entities
    policy_id: Optional[int] = None
    premium_id: Optional[int] = None
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class PaymentSimulationRequest(BaseModel):
    """Schema for payment simulation request."""
    virtual_account_number: str
    amount: Decimal

class PaymentSimulationResponse(BaseModel):
    success: bool
    message: str
    data: dict = {}

class VirtualAccountWebhook(BaseModel):
    """Schema for processing Squad webhook data."""
    transaction_reference: str
    virtual_account_number: str
    principal_amount: str
    settled_amount: str
    fee_charged: str
    transaction_date: str
    customer_identifier: str
    transaction_indicator: str
    remarks: str
    currency: str = "NGN"
    channel: str = "virtual-account"
    sender_name: Optional[str] = None

class BrokerPerformanceMetrics(BaseModel):
    """Schema for broker performance metrics."""
    total_credits: Decimal
    total_commission_earned: Decimal  # This would be separate broker commissions, not platform commission
    total_accounts: int
    active_accounts: int
    average_balance: Decimal

class CommissionSummary(BaseModel):
    """Schema for platform commission summary."""
    total_commission_pool: Decimal
    insureflow_commission: Decimal  # 0.75% of transactions
    habari_commission: Decimal      # 0.25% of transactions
    platform_commission_rate: Decimal
    insureflow_rate: Decimal
    habari_rate: Decimal 