"""
Virtual Account Transaction model for InsureFlow application.
Tracks all transactions for Squad Co virtual accounts.
"""
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Enum, Boolean, Text
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class TransactionType(enum.Enum):
    """Transaction type enumeration."""
    CREDIT = "credit"
    DEBIT = "debit"
    COMMISSION = "commission"
    SETTLEMENT = "settlement"
    REFUND = "refund"


class TransactionStatus(enum.Enum):
    """Transaction status enumeration."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REVERSED = "reversed"


class TransactionIndicator(enum.Enum):
    """Transaction flow indicator."""
    C = "C"  # Credit (money in)
    D = "D"  # Debit (money out)


class VirtualAccountTransaction(Base):
    """Transaction model for virtual account operations."""
    
    __tablename__ = "virtual_account_transactions"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Relationships - Foreign Keys
    virtual_account_id = Column(Integer, ForeignKey("virtual_accounts.id"), nullable=False, index=True)
    policy_id = Column(Integer, ForeignKey("policies.id"), nullable=True, index=True)  # Link to related policy
    premium_id = Column(Integer, ForeignKey("premiums.id"), nullable=True, index=True)  # Link to related premium
    
    # Squad Co Transaction Details
    transaction_reference = Column(String(100), unique=True, index=True, nullable=False)
    squad_transaction_reference = Column(String(100), nullable=True)  # Squad's internal reference
    
    # Transaction Information
    transaction_type = Column(
        Enum(TransactionType, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False
    )
    transaction_indicator = Column(
        Enum(TransactionIndicator, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False
    )
    status = Column(
        Enum(TransactionStatus, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        default=TransactionStatus.PENDING.value
    )
    
    # Financial Details
    principal_amount = Column(Numeric(15, 2), nullable=False)  # Original amount
    settled_amount = Column(Numeric(15, 2), nullable=False)    # Amount after fees
    fee_charged = Column(Numeric(10, 2), nullable=False, default=0)
    total_platform_commission = Column(Numeric(10, 2), nullable=False, default=0)  # Total 1% commission
    insureflow_commission = Column(Numeric(10, 2), nullable=False, default=0)  # 0.75% to InsureFlow
    habari_commission = Column(Numeric(10, 2), nullable=False, default=0)  # 0.25% to Habari
    
    # Transaction Context
    currency = Column(String(3), nullable=False, default="NGN")
    channel = Column(String(50), nullable=False, default="virtual-account")
    sender_name = Column(String(255), nullable=True)
    remarks = Column(Text, nullable=True)
    
    # Processing Information
    transaction_date = Column(DateTime, nullable=False)
    merchant_settlement_date = Column(DateTime, nullable=True)
    alerted_merchant = Column(Boolean, default=False, nullable=False)
    
    # Freeze/Hold Information
    frozen_transaction = Column(Boolean, default=False, nullable=False)
    freeze_transaction_ref = Column(String(100), nullable=True)
    reason_for_frozen_transaction = Column(Text, nullable=True)
    
    # Webhook and Notification
    webhook_received_at = Column(DateTime, nullable=True)
    notification_sent = Column(Boolean, default=False, nullable=False)
    
    # Additional metadata
    transaction_metadata = Column(Text, nullable=True)  # JSON string for additional data
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    virtual_account = relationship("VirtualAccount", back_populates="transactions")
    policy = relationship("Policy", foreign_keys=[policy_id])
    premium = relationship("Premium", foreign_keys=[premium_id])
    
    @property
    def net_amount_to_user(self) -> Decimal:
        """Calculate net amount that goes to user after all commission deductions."""
        return self.settled_amount - self.total_platform_commission
    
    @property
    def commission_split_valid(self) -> bool:
        """Verify that commission split adds up correctly."""
        return abs(self.insureflow_commission + self.habari_commission - self.total_platform_commission) < Decimal('0.01')
    
    @property
    def is_settlement_ready(self) -> bool:
        """Check if transaction is ready for settlement."""
        return (
            self.status == TransactionStatus.COMPLETED and
            self.transaction_indicator == TransactionIndicator.C and
            not self.frozen_transaction and
            self.merchant_settlement_date is None
        )
    
    def __repr__(self):
        return f"<VirtualAccountTransaction(id={self.id}, ref='{self.transaction_reference}', type='{self.transaction_type.value}', amount={self.principal_amount})>" 