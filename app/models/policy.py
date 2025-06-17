"""
Policy model for InsureFlow application.
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class PolicyStatus(enum.Enum):
    """Policy status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    PENDING = "pending"


class PolicyType(enum.Enum):
    """Policy type enumeration."""
    LIFE = "life"
    HEALTH = "health"
    AUTO = "auto"
    HOME = "home"
    BUSINESS = "business"
    TRAVEL = "travel"


class Policy(Base):
    """Policy model for managing insurance policies."""
    
    __tablename__ = "policies"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Policy identification
    policy_number = Column(String(100), unique=True, index=True, nullable=False)
    policy_type = Column(Enum(PolicyType), nullable=False)
    
    # Relationships - Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    company_id = Column(Integer, ForeignKey("insurance_companies.id"), nullable=False, index=True)
    broker_id = Column(Integer, ForeignKey("brokers.id"), nullable=True, index=True)
    
    # Policy details
    status = Column(Enum(PolicyStatus), nullable=False, default=PolicyStatus.PENDING)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    
    # Coverage information (stored as JSON text for flexibility)
    coverage_details = Column(Text, nullable=True)  # Will store JSON string
    coverage_amount = Column(String(20), nullable=True)  # Storing as string to handle currency
    
    # Additional information
    terms_and_conditions = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="policies")
    company = relationship("InsuranceCompany", back_populates="policies")
    broker = relationship("Broker", back_populates="policies")
    premiums = relationship("Premium", back_populates="policy", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Policy(id={self.id}, number='{self.policy_number}', type='{self.policy_type.value}', status='{self.status.value}')>" 