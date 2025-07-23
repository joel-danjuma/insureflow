#!/usr/bin/env python3
"""
Script to create an initial InsureFlow platform admin user.
This script should be run after setting up the database to create the first admin user.
"""
import sys
import os
from getpass import getpass

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.crud import user as crud_user


def create_admin_user():
    """Create an initial InsureFlow platform admin user."""
    
    print("🔐 InsureFlow Platform Admin User Creation")
    print("=" * 50)
    
    # Get database session
    db: Session = SessionLocal()
    
    try:
        # Check if any admin users already exist
        existing_admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
        if existing_admin:
            print(f"❌ Platform admin user already exists: {existing_admin.email}")
            print("   Delete existing admin user first if you want to create a new one.")
            return
        
        # Get user input
        print("\n📝 Enter details for the new platform admin user:")
        email = input("Email: ").strip()
        if not email:
            print("❌ Email is required!")
            return
        
        # Check if email already exists
        existing_user = crud_user.get_user_by_email(db, email=email)
        if existing_user:
            print(f"❌ User with email {email} already exists!")
            return
        
        username = input("Username: ").strip()
        if not username:
            username = email.split('@')[0]  # Default to email prefix
        
        # Check if username already exists
        existing_user = crud_user.get_user_by_username(db, username=username)
        if existing_user:
            print(f"❌ User with username {username} already exists!")
            return
        
        full_name = input("Full Name: ").strip()
        if not full_name:
            full_name = "InsureFlow Administrator"
        
        # Get password (hidden input)
        print("\n🔑 Password setup:")
        password = getpass("Enter password: ")
        if len(password) < 8:
            print("❌ Password must be at least 8 characters long!")
            return
        
        password_confirm = getpass("Confirm password: ")
        if password != password_confirm:
            print("❌ Passwords do not match!")
            return
        
        # Create the admin user
        print(f"\n⏳ Creating admin user...")
        
        hashed_password = get_password_hash(password)
        
        admin_user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True,
            can_create_policies=True,
            can_make_payments=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print(f"✅ Successfully created InsureFlow platform admin user!")
        print(f"   👤 Username: {username}")
        print(f"   📧 Email: {email}")
        print(f"   🏷️  Role: {UserRole.ADMIN.value}")
        print(f"   🆔 User ID: {admin_user.id}")
        
        print(f"\n🎯 This user can now access the InsureFlow admin dashboard at:")
        print(f"   📊 /api/v1/admin/insureflow/dashboard")
        print(f"   📋 /api/v1/admin/insureflow/transactions/logs")
        print(f"   💰 /api/v1/admin/insureflow/analytics/commission")
        print(f"   🔧 /api/v1/admin/insureflow/system/health-check")
        
        print(f"\n⚠️  Important Security Notes:")
        print(f"   • This user has access to sensitive platform revenue data")
        print(f"   • Only InsureFlow platform administrators should have this role")
        print(f"   • Insurance and broker admins cannot access these endpoints")
        print(f"   • Consider enabling additional security measures (2FA, IP restrictions)")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating admin user: {str(e)}")
    finally:
        db.close()


if __name__ == "__main__":
    create_admin_user() 