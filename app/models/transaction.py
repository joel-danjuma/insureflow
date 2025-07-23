"""
Transaction model for InsureFlow application.
"""
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Enum, Text, Boolean
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class TransactionType(enum.Enum):
    """Transaction type enumeration."""
    PREMIUM_PAYMENT = "premium_payment"
    CLAIM_PAYOUT = "claim_payout"
    COMMISSION_PAYMENT = "commission_payment"
    REFUND = "refund"
    FEE = "fee"
    ADJUSTMENT = "adjustment"


class TransactionStatus(enum.Enum):
    """Transaction status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REVERSED = "reversed"


class Transaction(Base):
    """Transaction model for tracking all financial transactions."""
    
    __tablename__ = "transactions"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Transaction identification
    transaction_type = Column(Enum(TransactionType), nullable=False, index=True)
    transaction_reference = Column(String(255), unique=True, index=True, nullable=False)
    
    # Financial details
    amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="NGN")
    
    # Transaction processing
    transaction_date = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    status = Column(Enum(TransactionStatus), nullable=False, default=TransactionStatus.PENDING, index=True)
    
    # Related entities (optional foreign keys for flexible associations)
    related_user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    related_policy_id = Column(Integer, ForeignKey("policies.id"), nullable=True, index=True)
    related_premium_id = Column(Integer, ForeignKey("premiums.id"), nullable=True, index=True)
    related_payment_id = Column(Integer, ForeignKey("payments.id"), nullable=True, index=True)
    related_broker_id = Column(Integer, ForeignKey("brokers.id"), nullable=True, index=True)
    
    # Transaction details
    description = Column(Text, nullable=False)
    notes = Column(Text, nullable=True)
    
    # External references
    external_reference = Column(String(255), nullable=True)
    batch_reference = Column(String(255), nullable=True, index=True)  # For grouped transactions
    
    # Processing information
    processed_by = Column(String(255), nullable=True)  # System or user who processed
    processing_method = Column(String(100), nullable=True)  # e.g., "automatic", "manual", "webhook"
    
    # Reconciliation
    is_reconciled = Column(Boolean, default=False, nullable=False, index=True)
    reconciled_date = Column(DateTime, nullable=True)
    reconciled_by = Column(String(255), nullable=True)
    
    # Accounting information
    debit_account = Column(String(100), nullable=True)
    credit_account = Column(String(100), nullable=True)
    
    # Failure information
    failure_reason = Column(Text, nullable=True)
    retry_count = Column(Integer, nullable=False, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    related_user = relationship("User", foreign_keys=[related_user_id])
    related_policy = relationship("Policy", foreign_keys=[related_policy_id])
    related_premium = relationship("Premium", foreign_keys=[related_premium_id])
    related_payment = relationship("Payment", foreign_keys=[related_payment_id])
    related_broker = relationship("Broker", foreign_keys=[related_broker_id])
    
    @property
    def is_completed(self) -> bool:
        """Check if transaction is completed."""
        return self.status == TransactionStatus.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """Check if transaction failed."""
        return self.status in [TransactionStatus.FAILED, TransactionStatus.CANCELLED]
    
    @property
    def display_amount(self) -> str:
        """Format amount for display."""
        return f"{self.currency} {self.amount:,.2f}"
    
    def __repr__(self):
        return f"<Transaction(id={self.id}, type='{self.transaction_type.value}', amount={self.amount}, status='{self.status.value}', ref='{self.transaction_reference}')>" 