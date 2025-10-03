"""
Insurance Company model for InsureFlow application.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class InsuranceCompany(Base):
    """Insurance Company model for managing insurance providers."""
    
    __tablename__ = "insurance_companies"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Company identification
    name = Column(String(255), unique=True, index=True, nullable=False)
    registration_number = Column(String(100), unique=True, index=True, nullable=False)
    
    # Contact information
    address = Column(Text, nullable=True)
    contact_email = Column(String(255), nullable=False)
    contact_phone = Column(String(50), nullable=True)
    
    # Company details
    website = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    
    # Settlement account details for GAPS transfers
    settlement_account_number = Column(String(20), nullable=True, index=True)
    settlement_bank_code = Column(String(10), nullable=True)
    settlement_account_name = Column(String(255), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    policies = relationship("Policy", back_populates="company")
    brokers = relationship("Broker", back_populates="company")
    
    def __repr__(self):
        return f"<InsuranceCompany(id={self.id}, name='{self.name}', registration='{self.registration_number}')>" 