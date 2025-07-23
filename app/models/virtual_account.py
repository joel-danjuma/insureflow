"""
Virtual Account model for InsureFlow application.
Handles Squad Co virtual accounts for automated fund distribution.
"""
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Enum, Boolean, Text
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class VirtualAccountType(enum.Enum):
    """Virtual account type enumeration."""
    INDIVIDUAL = "individual"
    BUSINESS = "business"


class VirtualAccountStatus(enum.Enum):
    """Virtual account status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    CLOSED = "closed"


class VirtualAccount(Base):
    """Virtual Account model for managing Squad Co virtual accounts."""
    
    __tablename__ = "virtual_accounts"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Relationships - Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Squad Co Virtual Account Details
    customer_identifier = Column(String(100), unique=True, index=True, nullable=False)
    virtual_account_number = Column(String(20), unique=True, index=True, nullable=False)
    bank_code = Column(String(10), nullable=False, default="058")  # Squad's bank code
    
    # Account Information
    account_type = Column(Enum(VirtualAccountType), nullable=False)
    status = Column(Enum(VirtualAccountStatus), nullable=False, default=VirtualAccountStatus.ACTIVE)
    
    # Individual Account Fields (when account_type = INDIVIDUAL)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    middle_name = Column(String(100), nullable=True)
    bvn = Column(String(11), nullable=True)
    date_of_birth = Column(String(20), nullable=True)  # DD/MM/YYYY format for Squad
    gender = Column(String(1), nullable=True)  # 1 for male, 2 for female
    
    # Business Account Fields (when account_type = BUSINESS)
    business_name = Column(String(255), nullable=True)
    
    # Common Fields
    mobile_number = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    address = Column(Text, nullable=True)
    
    # Financial Tracking
    total_credits = Column(Numeric(15, 2), nullable=False, default=0)
    total_debits = Column(Numeric(15, 2), nullable=False, default=0)
    current_balance = Column(Numeric(15, 2), nullable=False, default=0)
    
    # Squad Co Response Data
    beneficiary_account = Column(String(50), nullable=True)
    squad_created_at = Column(DateTime, nullable=True)
    squad_updated_at = Column(DateTime, nullable=True)
    
    # Commission and Settlement Configuration
    platform_commission_rate = Column(Numeric(5, 4), nullable=False, default=0.01)  # 1% total platform commission
    insureflow_commission_rate = Column(Numeric(5, 4), nullable=False, default=0.0075)  # 0.75% to InsureFlow
    habari_commission_rate = Column(Numeric(5, 4), nullable=False, default=0.0025)  # 0.25% to Habari
    auto_settlement = Column(Boolean, default=True, nullable=False)
    settlement_threshold = Column(Numeric(10, 2), nullable=False, default=1000)  # Minimum amount for settlement
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_activity_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="virtual_accounts")
    transactions = relationship("VirtualAccountTransaction", back_populates="virtual_account", cascade="all, delete-orphan")
    
    @property
    def net_amount_after_commission(self) -> Decimal:
        """Calculate net amount after platform commission deduction."""
        return self.current_balance * (1 - self.platform_commission_rate)
    
    @property
    def habari_commission_amount(self) -> Decimal:
        """Calculate total commission amount for Habari (0.25%)."""
        return self.total_credits * self.habari_commission_rate
    
    @property
    def insureflow_commission_amount(self) -> Decimal:
        """Calculate total commission amount for InsureFlow (0.75%)."""
        return self.total_credits * self.insureflow_commission_rate
    
    @property
    def total_platform_commission(self) -> Decimal:
        """Calculate total platform commission (1%)."""
        return self.total_credits * self.platform_commission_rate
    
    @property
    def display_name(self) -> str:
        """Get display name based on account type."""
        if self.account_type == VirtualAccountType.BUSINESS:
            return self.business_name or "Business Account"
        else:
            return f"{self.first_name or ''} {self.last_name or ''}".strip() or "Individual Account"
    
    def __repr__(self):
        return f"<VirtualAccount(id={self.id}, customer_id='{self.customer_identifier}', account_number='{self.virtual_account_number}', type='{self.account_type.value}')>" 