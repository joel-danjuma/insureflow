"""
User model for InsureFlow application.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class UserRole(enum.Enum):
    """User role enumeration."""
    ADMIN = "ADMIN"
    BROKER = "BROKER"
    CUSTOMER = "CUSTOMER"
    INSURANCE_ADMIN = "INSURANCE_ADMIN"
    INSURANCE_ACCOUNTANT = "INSURANCE_ACCOUNTANT"
    BROKER_ADMIN = "BROKER_ADMIN"
    BROKER_ACCOUNTANT = "BROKER_ACCOUNTANT"


class User(Base):
    """User model for authentication and user management."""
    
    __tablename__ = "users"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Authentication fields
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # User information
    full_name = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.CUSTOMER)
    
    # Additional user details for enhanced registration
    phone_number = Column(String(50), nullable=True)
    organization_name = Column(String(100), nullable=True)  # Company/Organization name
    bvn = Column(String(11), nullable=True)  # Bank Verification Number for Nigerian users
    date_of_birth = Column(DateTime, nullable=True)
    gender = Column(String(10), nullable=True)
    address = Column(String(500), nullable=True)
    
    # Status and tracking
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    can_create_policies = Column(Boolean, default=False, nullable=False)  # For Insurance Accountants
    can_make_payments = Column(Boolean, default=False, nullable=False)  # For Broker Accountants
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    policies = relationship("Policy", back_populates="user")
    broker_profile = relationship("Broker", back_populates="user", uselist=False)
    notifications = relationship("Notification", back_populates="broker", foreign_keys="Notification.broker_id")
    virtual_accounts = relationship("VirtualAccount", back_populates="user", cascade="all, delete-orphan")
    
    @property
    def is_insurance_user(self) -> bool:
        """Check if user belongs to insurance company roles."""
        return self.role in [UserRole.INSURANCE_ADMIN, UserRole.INSURANCE_ACCOUNTANT]
    
    @property
    def is_broker_user(self) -> bool:
        """Check if user belongs to broker roles."""
        return self.role in [UserRole.BROKER, UserRole.BROKER_ADMIN, UserRole.BROKER_ACCOUNTANT]
    
    @property
    def can_perform_admin_actions(self) -> bool:
        """Check if user can perform administrative actions."""
        return self.role in [UserRole.ADMIN, UserRole.INSURANCE_ADMIN, UserRole.BROKER_ADMIN]
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role.value}')>" 