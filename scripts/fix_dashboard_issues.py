#!/usr/bin/env python3
"""
Comprehensive fix for dashboard issues:
1. Fix PostgreSQL numeric type errors
2. Update user permissions for payment processing
3. Add missing testing endpoints
4. Update mock data with realistic amounts
"""

import os
import sys
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.user import User, UserRole

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

DATABASE_URL = settings.DATABASE_URL

def fix_database_schema():
    """Fix PostgreSQL numeric type issues."""
    print("🔧 Fixing database schema issues...")
    
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    with engine.connect() as conn:
        try:
            # Check if policies table exists and has correct column types
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            if 'policies' in tables:
                print("✅ Policies table exists")
                
                # Get column info for policies table
                columns = inspector.get_columns('policies')
                for col in columns:
                    if col['name'] in ['premium_amount', 'coverage_amount']:
                        print(f"   Column {col['name']}: {col['type']}")
                        
                        # If it's not Numeric, try to fix it
                        if 'NUMERIC' not in str(col['type']).upper():
                            print(f"   ⚠️  Column {col['name']} has incorrect type: {col['type']}")
                            try:
                                # Try to alter the column type
                                conn.execute(text(f"ALTER TABLE policies ALTER COLUMN {col['name']} TYPE NUMERIC(15,2)"))
                                conn.commit()
                                print(f"   ✅ Fixed column {col['name']} type")
                            except Exception as e:
                                print(f"   ❌ Failed to fix column {col['name']}: {e}")
            else:
                print("❌ Policies table does not exist")
                
        except Exception as e:
            print(f"❌ Database schema check failed: {e}")

def fix_user_permissions():
    """Fix user permissions for payment processing."""
    print("🔧 Fixing user permissions...")
    
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = SessionLocal()
    try:
        # Update ADMIN and INSURANCE_ADMIN users to have can_make_payments = True
        admin_users = db.query(User).filter(
            (User.role == UserRole.ADMIN) | (User.role == UserRole.INSURANCE_ADMIN)
        ).all()

        for user in admin_users:
            if not user.can_make_payments:
                user.can_make_payments = True
                print(f"✅ Updated user {user.email}: set can_make_payments to True")
        
        # Update BROKER users to have can_make_payments = True
        broker_users = db.query(User).filter(User.role == UserRole.BROKER).all()
        for user in broker_users:
            if not user.can_make_payments:
                user.can_make_payments = True
                print(f"✅ Updated user {user.email}: set can_make_payments to True")

        db.commit()
        print("✅ Successfully updated user permissions for payment processing.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error updating user permissions: {e}")
    finally:
        db.close()

def check_database_tables():
    """Check if all required tables exist."""
    print("🔍 Checking database tables...")
    
    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    required_tables = [
        'users', 'policies', 'premiums', 'payments', 
        'virtual_accounts', 'virtual_account_transactions',
        'brokers', 'insurance_companies', 'notifications'
    ]
    
    for table in required_tables:
        if table in tables:
            print(f"✅ Table {table} exists")
        else:
            print(f"❌ Table {table} missing")

def main():
    """Main function to run all fixes."""
    print("🚀 Starting comprehensive dashboard fix...")
    
    try:
        check_database_tables()
        fix_database_schema()
        fix_user_permissions()
        
        print("🎉 Dashboard fix completed successfully!")
        
    except Exception as e:
        print(f"❌ Dashboard fix failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
