"""
Policy model for InsureFlow application.
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey, Text, Enum, Float, Boolean, Numeric
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


class PaymentFrequency(enum.Enum):
    """Payment frequency enumeration."""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUALLY = "annually"
    CUSTOM = "custom"


class Policy(Base):
    """Policy model for managing insurance policies."""
    
    __tablename__ = "policies"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Policy identification
    policy_name = Column(String(255), nullable=False)  # Human readable policy name
    policy_number = Column(String(100), unique=True, index=True, nullable=False)
    policy_type = Column(Enum(PolicyType), nullable=False)
    
    # Relationships - Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    company_id = Column(Integer, ForeignKey("insurance_companies.id"), nullable=False, index=True)
    broker_id = Column(Integer, ForeignKey("brokers.id"), nullable=True, index=True)
    
    # Policy details
    status = Column(Enum(PolicyStatus), nullable=False, default=PolicyStatus.PENDING)
    start_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)  # When policy expires or needs renewal
    end_date = Column(Date, nullable=False)
    duration_months = Column(Integer, nullable=True)  # Duration in months for easier calculations
    reminder_sent_at = Column(DateTime, nullable=True)
    
    # Payment & Premium Details
    premium_amount = Column(Numeric(15, 2), nullable=False)  # Main premium amount
    payment_frequency = Column(Enum(PaymentFrequency), nullable=False, default=PaymentFrequency.MONTHLY)
    first_payment_date = Column(Date, nullable=True)
    last_payment_date = Column(Date, nullable=True)
    grace_period_days = Column(Integer, nullable=False, default=30)
    custom_payment_schedule = Column(Text, nullable=True)  # JSON for custom payment schedules
    
    # Policyholder Information
    company_name = Column(String(255), nullable=False)  # Insured company name
    contact_person = Column(String(255), nullable=False)  # Primary contact person
    contact_email = Column(String(255), nullable=False)
    contact_phone = Column(String(50), nullable=True)
    rc_number = Column(String(100), nullable=True)  # Registration/Tax ID
    
    # Coverage Details
    coverage_amount = Column(Numeric(15, 2), nullable=False)  # Total coverage amount
    coverage_items = Column(Text, nullable=True)  # JSON list of covered items/risks
    beneficiaries = Column(Text, nullable=True)  # JSON list of beneficiaries with shares
    coverage_details = Column(Text, nullable=True)  # Additional coverage description
    
    # Broker Visibility & Tags
    broker_notes = Column(Text, nullable=True)  # Notes visible to assigned broker
    internal_tags = Column(Text, nullable=True)  # JSON array of tags for categorization
    
    # Advanced Settings
    auto_renew = Column(Boolean, default=False, nullable=False)
    notify_broker_on_change = Column(Boolean, default=True, nullable=False)
    commission_structure = Column(Text, nullable=True)  # JSON for custom commission rates
    
    # Document Management
    policy_documents = Column(Text, nullable=True)  # JSON array of document references
    kyc_documents = Column(Text, nullable=True)  # JSON array of KYC document references
    
    # Additional information
    terms_and_conditions = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)  # General internal notes
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="policies")
    company = relationship("InsuranceCompany", back_populates="policies")
    broker = relationship("Broker", back_populates="policies")
    premiums = relationship("Premium", back_populates="policy", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="policy")
    
    merchant_reference = Column(String, unique=True, index=True, nullable=True)
    payment_status = Column(String, default="pending")
    transaction_reference = Column(String, unique=True, index=True, nullable=True)
    
    def __repr__(self):
        return f"<Policy(id={self.id}, name='{self.policy_name}', number='{self.policy_number}', type='{self.policy_type.value}', status='{self.status.value}')>" 