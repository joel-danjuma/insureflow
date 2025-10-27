"""
Payment model for InsureFlow application.
"""
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Enum, Text
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class PaymentMethod(enum.Enum):
    """Payment method enumeration."""
    CARD = "CARD"
    BANK_TRANSFER = "BANK_TRANSFER"
    USSD = "USSD"
    WALLET = "WALLET"
    CASH = "CASH"


class PaymentTransactionStatus(enum.Enum):
    """Payment transaction status enumeration."""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    REFUNDED = "REFUNDED"


class Payment(Base):
    """Payment model for tracking transactions."""
    
    __tablename__ = "payments"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Relationships - Foreign Keys
    premium_id = Column(Integer, ForeignKey("premiums.id"), nullable=False, index=True)
    
    # Payment details
    amount_paid = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="NGN")
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    
    # Payment processing
    payment_date = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    status = Column(Enum(PaymentTransactionStatus), nullable=False, default=PaymentTransactionStatus.PENDING, index=True)
    
    # External references (Squad Co and other gateways)
    transaction_reference = Column(String(255), unique=True, index=True, nullable=False)
    external_reference = Column(String(255), nullable=True)  # Gateway's reference
    gateway_response = Column(Text, nullable=True)  # Store JSON response
    
    # Squad Co specific fields
    squad_transaction_id = Column(String(100), nullable=True)
    squad_payment_ref = Column(String(100), nullable=True)
    
    # Additional payment information
    payer_name = Column(String(255), nullable=True)
    payer_email = Column(String(255), nullable=True)
    payer_phone = Column(String(50), nullable=True)
    
    # Processing details
    processing_fee = Column(Numeric(10, 2), nullable=True, default=0)
    net_amount = Column(Numeric(10, 2), nullable=True)  # Amount after fees
    
    # Failure information
    failure_reason = Column(Text, nullable=True)
    retry_count = Column(Integer, nullable=False, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    processed_at = Column(DateTime, nullable=True)
    
    # Relationships
    premium = relationship("Premium", back_populates="payments")
    
    @property
    def is_successful(self) -> bool:
        """Check if payment was successful."""
        return self.status == PaymentTransactionStatus.SUCCESS
    
    @property
    def is_pending(self) -> bool:
        """Check if payment is still pending."""
        return self.status in [PaymentTransactionStatus.PENDING, PaymentTransactionStatus.PROCESSING]
    
    def __repr__(self):
        return f"<Payment(id={self.id}, premium_id={self.premium_id}, amount={self.amount_paid}, status='{self.status.value}', ref='{self.transaction_reference}')>" 