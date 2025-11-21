"""
Script to create a test broker user with known credentials.
This is useful for testing and development purposes.
"""
import sys
import os

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.crud import user as crud_user
from app.schemas.auth import UserCreate
from app.models.user import UserRole


def create_test_broker():
    """Create a test broker user with known credentials."""
    db: Session = SessionLocal()
    try:
        # Check if user already exists
        existing = crud_user.get_user_by_email(db, email="test@insureflow.com")
        if existing:
            print("✅ Test user already exists!")
            print(f"📧 Email: test@insureflow.com")
            print(f"🔑 Password: TestPassword123!")
            print(f"👤 User ID: {existing.id}")
            print(f"🎭 Role: {existing.role.value}")
            return
        
        # Create test user
        user_data = UserCreate(
            username="testbroker",
            email="test@insureflow.com",
            password="TestPassword123!",
            full_name="Test Broker",
            role="BROKER"
        )
        
        new_user = crud_user.create_user(db, obj_in=user_data)
        print("✅ Test user created successfully!")
        print(f"📧 Email: test@insureflow.com")
        print(f"🔑 Password: TestPassword123!")
        print(f"👤 User ID: {new_user.id}")
        print(f"🎭 Role: {new_user.role.value}")
        print("\nYou can now login with these credentials to access the application.")
        
    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    print("🚀 Creating test broker user...")
    print("-" * 50)
    create_test_broker()
    print("-" * 50)

