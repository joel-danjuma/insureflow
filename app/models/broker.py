"""
Broker model for InsureFlow application.
"""
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Numeric, Boolean
from sqlalchemy.orm import relationship

from app.core.database import Base


class Broker(Base):
    """Broker model for managing insurance brokers."""
    
    __tablename__ = "brokers"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Broker identification
    name = Column(String(255), nullable=False, index=True)
    license_number = Column(String(100), unique=True, index=True, nullable=False)
    agency_name = Column(String(255), nullable=True)
    
    # Relationships - Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, unique=True)  # Link to user account
    company_id = Column(Integer, ForeignKey("insurance_companies.id"), nullable=True, index=True)  # Primary company
    
    # Contact information
    contact_email = Column(String(255), nullable=False)
    contact_phone = Column(String(50), nullable=True)
    office_address = Column(Text, nullable=True)
    
    # Business details
    specialization = Column(String(255), nullable=True)  # e.g., "Life Insurance, Health Insurance"
    experience_years = Column(Integer, nullable=True)
    territory = Column(String(255), nullable=True)  # Geographic coverage area
    
    # Commission configuration
    default_commission_rate = Column(Numeric(5, 4), nullable=True)  # e.g., 0.1250 for 12.5%
    commission_type = Column(String(50), nullable=False, default="percentage")  # percentage or fixed
    
    # Performance tracking
    total_policies_sold = Column(Integer, nullable=False, default=0)
    total_premiums_collected = Column(Numeric(15, 2), nullable=False, default=0)
    total_commission_earned = Column(Numeric(15, 2), nullable=False, default=0)
    
    # Status and verification
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    verification_date = Column(DateTime, nullable=True)
    
    # License and certification
    license_expiry_date = Column(DateTime, nullable=True)
    certifications = Column(Text, nullable=True)  # JSON string of certifications
    
    # Additional information
    bio = Column(Text, nullable=True)
    website = Column(String(255), nullable=True)
    social_media = Column(Text, nullable=True)  # JSON string of social media links
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_activity = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="broker_profile")
    company = relationship("InsuranceCompany", back_populates="brokers")
    policies = relationship("Policy", back_populates="broker")
    # commissions = relationship("Commission", back_populates="broker")
    
    @property
    def average_commission_per_policy(self) -> Decimal:
        """Calculate average commission per policy."""
        if self.total_policies_sold == 0:
            return Decimal('0')
        return self.total_commission_earned / self.total_policies_sold
    
    @property
    def is_license_valid(self) -> bool:
        """Check if broker license is still valid."""
        if not self.license_expiry_date:
            return True  # No expiry date set
        return datetime.utcnow() <= self.license_expiry_date
    
    def __repr__(self):
        return f"<Broker(id={self.id}, name='{self.name}', license='{self.license_number}', active={self.is_active})>" 