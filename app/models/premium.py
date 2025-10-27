"""
Premium model for InsureFlow application.
"""
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey, Numeric, Enum
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class PaymentStatus(enum.Enum):
    """Premium payment status enumeration."""
    PAID = "PAID"
    PENDING = "PENDING"
    OVERDUE = "OVERDUE"
    CANCELLED = "CANCELLED"
    REFUNDED = "REFUNDED"


class BillingCycle(enum.Enum):
    """Billing cycle enumeration."""
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    SEMI_ANNUAL = "SEMI_ANNUAL"
    ANNUAL = "ANNUAL"


class Premium(Base):
    """Premium model for managing policy premiums."""
    
    __tablename__ = "premiums"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Relationships - Foreign Keys
    policy_id = Column(Integer, ForeignKey("policies.id"), nullable=False, index=True)
    
    # Premium details
    amount = Column(Numeric(10, 2), nullable=False)  # Decimal for precise currency calculations
    currency = Column(String(3), nullable=False, default="NGN")  # ISO currency code
    
    # Payment scheduling
    due_date = Column(Date, nullable=False, index=True)
    billing_cycle = Column(Enum(BillingCycle), nullable=False, default=BillingCycle.MONTHLY)
    
    # Status tracking
    payment_status = Column(Enum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING, index=True)
    
    # Payment information
    paid_amount = Column(Numeric(10, 2), nullable=True, default=0)
    payment_date = Column(Date, nullable=True)
    
    # Grace period and late fees
    grace_period_days = Column(Integer, nullable=False, default=30)
    late_fee_amount = Column(Numeric(10, 2), nullable=True, default=0)
    
    # Reference information
    premium_reference = Column(String(100), unique=True, index=True, nullable=True)
    payment_reference = Column(String(100), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    policy = relationship("Policy", back_populates="premiums")
    payments = relationship("Payment", back_populates="premium", cascade="all, delete-orphan")
    
    @property
    def is_overdue(self) -> bool:
        """Check if premium is overdue."""
        if self.payment_status == PaymentStatus.PAID:
            return False
        
        today = date.today()
        grace_period_end = self.due_date + datetime.timedelta(days=self.grace_period_days)
        return today > grace_period_end
    
    @property
    def outstanding_amount(self) -> Decimal:
        """Calculate outstanding amount."""
        paid = self.paid_amount or Decimal('0')
        return self.amount - paid
    
    def __repr__(self):
        return f"<Premium(id={self.id}, policy_id={self.policy_id}, amount={self.amount}, status='{self.payment_status.value}', due_date='{self.due_date}')>" 