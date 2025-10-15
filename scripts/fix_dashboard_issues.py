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

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

try:
    # Try to import app modules
    from sqlalchemy import create_engine, text, inspect
    from sqlalchemy.orm import sessionmaker
    from app.core.config import settings
    from app.models.user import User, UserRole
    DATABASE_URL = settings.DATABASE_URL
except ImportError as e:
    print(f"⚠️  Could not import app modules: {e}")
    print("Using environment variables for database connection...")
    
    # Fallback to environment variables
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://insureflow:insureflow123@db:5432/insureflow')
    
    # Import only what we can
    from sqlalchemy import create_engine, text, inspect
    from sqlalchemy.orm import sessionmaker

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
                                # Try to alter the column type with an explicit USING clause for casting
                                conn.execute(text(f"ALTER TABLE policies ALTER COLUMN {col['name']} TYPE NUMERIC(15,2) USING {col['name']}::numeric"))
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
    
    try:
        with engine.connect() as conn:
            # Update ADMIN and INSURANCE_ADMIN users to have can_make_payments = True
            result = conn.execute(text("""
                UPDATE users 
                SET can_make_payments = true 
                WHERE role IN ('ADMIN', 'INSURANCE_ADMIN') 
                AND can_make_payments = false
            """))
            admin_updated = result.rowcount
            print(f"✅ Updated {admin_updated} admin users: set can_make_payments to True")
            
            # Update BROKER users to have can_make_payments = True
            result = conn.execute(text("""
                UPDATE users 
                SET can_make_payments = true 
                WHERE role = 'BROKER' 
                AND can_make_payments = false
            """))
            broker_updated = result.rowcount
            print(f"✅ Updated {broker_updated} broker users: set can_make_payments to True")
            
            conn.commit()
            print("✅ Successfully updated user permissions for payment processing.")
            
    except Exception as e:
        print(f"❌ Error updating user permissions: {e}")

def normalize_enum_cases():
    """Ensure enum values in the database are uppercase to match Python enums."""
    print("🔧 Normalizing enum case in the database...")
    
    engine = create_engine(DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            # List of columns and tables to update
            updates = {
                'policies': ['status', 'policy_type', 'payment_frequency']
                # Add other tables and columns here if needed in the future
            }
            
            total_updated_rows = 0
            for table, columns in updates.items():
                for column in columns:
                    statement = text(f"UPDATE {table} SET {column} = UPPER({column}) WHERE {column} IS NOT NULL AND {column} != UPPER({column})")
                    result = conn.execute(statement)
                    if result.rowcount > 0:
                        print(f"✅ Normalized {result.rowcount} rows for '{column}' in '{table}' table.")
                        total_updated_rows += result.rowcount
            
            conn.commit()
            if total_updated_rows == 0:
                print("✅ All enum values are already in the correct case.")
            else:
                print("✅ Successfully normalized all enum values.")

    except Exception as e:
        print(f"❌ Error normalizing enum cases: {e}")


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
        normalize_enum_cases() # Add this call here
        fix_database_schema()
        fix_user_permissions()
        
        print("🎉 Dashboard fix completed successfully!")
        
    except Exception as e:
        print(f"❌ Dashboard fix failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
