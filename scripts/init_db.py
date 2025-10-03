#!/usr/bin/env python3
"""
Database initialization script
Runs migrations and creates initial users if they don't exist
"""
import sys
import time
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import Base, get_db
from app.models.user import User, UserRole
from app.models.broker import Broker
from app.core.security import get_password_hash

def wait_for_db(max_retries=30, retry_interval=2):
    """Wait for database to be ready"""
    engine = create_engine(settings.DATABASE_URL)
    
    for attempt in range(max_retries):
        try:
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            print("✅ Database is ready!")
            return True
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"⏳ Waiting for database... (attempt {attempt + 1}/{max_retries})")
                time.sleep(retry_interval)
            else:
                print(f"❌ Database not ready after {max_retries} attempts")
                return False
    return False

def create_tables():
    """Create all tables from models"""
    try:
        from app.core.database import engine
        import app.models  # Import all models to register them
        
        print("📋 Creating database tables...")
        Base.metadata.create_all(bind=engine)
        
        # Check what tables were created
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"✅ Tables created: {', '.join(sorted(tables))}")
        return True
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

def create_initial_users():
    """Create initial users if they don't exist"""
    try:
        db = next(get_db())
        
        users_created = 0
        
        # Create Sarah Johnson (Insurance Admin)
        sarah = db.query(User).filter(User.email == 'sarah.johnson@sovereigntrust.com').first()
        if not sarah:
            sarah = User(
                email='sarah.johnson@sovereigntrust.com',
                username='sarah.johnson',
                full_name='Sarah Johnson',
                hashed_password=get_password_hash('password123'),
                role=UserRole.INSURANCE_ADMIN,
                is_active=True,
                is_verified=True
            )
            db.add(sarah)
            users_created += 1
            print("✅ Created Sarah Johnson (Insurance Admin)")
        else:
            print("ℹ️  Sarah Johnson already exists")
        
        # Create John Broker
        john_user = db.query(User).filter(User.email == 'john.broker@scib.ng').first()
        if not john_user:
            john_user = User(
                email='john.broker@scib.ng',
                username='john.broker',
                full_name='John Broker',
                hashed_password=get_password_hash('password123'),
                role=UserRole.BROKER,
                is_active=True,
                is_verified=True
            )
            db.add(john_user)
            db.flush()  # Get the ID
            
            # Create broker profile
            john_broker = Broker(
                user_id=john_user.id,
                name='SCIB',
                license_number='BRK-2023-001',
                agency_name='Sovereign Capital Investment Banking',
                contact_email='john.broker@scib.ng',
                contact_phone='+234-801-234-5678',
                office_address='Lagos, Nigeria',
                is_active=True
            )
            db.add(john_broker)
            users_created += 1
            print("✅ Created John Broker with profile")
        else:
            print("ℹ️  John Broker already exists")
        
        # Create Admin user
        admin = db.query(User).filter(User.email == 'admin@sovereigntrust.com').first()
        if not admin:
            admin = User(
                email='admin@sovereigntrust.com',
                username='admin',
                full_name='Admin User',
                hashed_password=get_password_hash('admin123'),
                role=UserRole.ADMIN,
                is_active=True,
                is_verified=True
            )
            db.add(admin)
            users_created += 1
            print("✅ Created Admin user")
        else:
            print("ℹ️  Admin user already exists")
        
        db.commit()
        
        # Show all users
        all_users = db.query(User).all()
        print(f"\n📊 Total users in database: {len(all_users)}")
        for user in all_users:
            print(f"   - {user.email} ({user.role.value})")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating users: {e}")
        if 'db' in locals():
            db.rollback()
            db.close()
        return False

def main():
    """Main initialization function"""
    print("🚀 Starting database initialization...")
    
    # Wait for database to be ready
    if not wait_for_db():
        print("❌ Database initialization failed - database not ready")
        sys.exit(1)
    
    # Create tables
    if not create_tables():
        print("❌ Database initialization failed - could not create tables")
        sys.exit(1)
    
    # Create initial users
    if not create_initial_users():
        print("❌ Database initialization failed - could not create users")
        sys.exit(1)
    
    print("\n✅ Database initialization completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())

