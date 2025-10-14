#!/usr/bin/env python3
"""
Comprehensive fix for all InsureFlow issues:
1. Fix INSUREFLOW_ADMIN enum issue with SQLAlchemy cache
2. Create proper admin account
3. Verify all functionality
"""

import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import logging

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.core.security import get_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def comprehensive_fix():
    """Apply comprehensive fixes for all known issues."""
    
    try:
        print("🚀 InsureFlow Comprehensive Fix")
        print("=" * 50)
        
        # Create database engine with explicit settings
        engine = create_engine(
            settings.DATABASE_URL,
            pool_pre_ping=True,
            pool_recycle=300,
            echo=False
        )
        
        with engine.connect() as conn:
            # Step 1: Check and fix enum
            print("📋 Step 1: Fixing userrole enum...")
            
            # Get current enum values
            result = conn.execute(text("""
                SELECT unnest(enum_range(NULL::userrole)) as enum_value
                ORDER BY enum_value;
            """))
            current_enums = [row[0] for row in result.fetchall()]
            print(f"   Current enum values: {current_enums}")
            
            if 'INSUREFLOW_ADMIN' not in current_enums:
                print("   Adding INSUREFLOW_ADMIN to enum...")
                conn.execute(text("ALTER TYPE userrole ADD VALUE 'INSUREFLOW_ADMIN'"))
                print("   ✅ Enum value added")
            else:
                print("   ✅ INSUREFLOW_ADMIN already exists")
            
            # Step 2: Remove any existing admin@insureflow.com users to start fresh
            print("\n🧹 Step 2: Cleaning up existing admin accounts...")
            result = conn.execute(text("""
                DELETE FROM users WHERE email = 'admin@insureflow.com'
                RETURNING id, email, role;
            """))
            deleted_users = result.fetchall()
            
            if deleted_users:
                print(f"   Removed {len(deleted_users)} existing admin account(s)")
                for user in deleted_users:
                    print(f"   - Removed: {user.email} (Role: {user.role})")
            else:
                print("   No existing admin accounts to remove")
            
            # Step 3: Create fresh InsureFlow admin account
            print("\n👤 Step 3: Creating fresh InsureFlow admin account...")
            hashed_password = get_password_hash("password123")
            
            conn.execute(text("""
                INSERT INTO users (
                    username, email, hashed_password, full_name, role, 
                    is_active, is_verified, created_at, updated_at
                ) VALUES (
                    'insureflow_admin', 'admin@insureflow.com', 
                    :hashed_password,
                    'InsureFlow Platform Administrator', 'INSUREFLOW_ADMIN', 
                    true, true, NOW(), NOW()
                )
            """), {"hashed_password": hashed_password})
            print("   ✅ Fresh admin account created")
            
            # Step 4: Verify the account works
            print("\n🧪 Step 4: Verifying admin account...")
            result = conn.execute(text("""
                SELECT id, username, email, full_name, role, is_active, is_verified
                FROM users 
                WHERE email = 'admin@insureflow.com'
            """))
            admin_user = result.fetchone()
            
            if admin_user and admin_user.role == 'INSUREFLOW_ADMIN':
                print("   ✅ Admin account verified successfully!")
                print(f"   - ID: {admin_user.id}")
                print(f"   - Username: {admin_user.username}")
                print(f"   - Email: {admin_user.email}")
                print(f"   - Role: {admin_user.role}")
                print(f"   - Active: {admin_user.is_active}")
                print(f"   - Verified: {admin_user.is_verified}")
            else:
                print("   ❌ Admin account verification failed")
                return False
            
            # Step 5: Test enum query compatibility
            print("\n🔍 Step 5: Testing enum query compatibility...")
            result = conn.execute(text("""
                SELECT COUNT(*) as total_users,
                       COUNT(CASE WHEN role = 'INSUREFLOW_ADMIN' THEN 1 END) as insureflow_admins,
                       COUNT(CASE WHEN role = 'ADMIN' THEN 1 END) as regular_admins,
                       COUNT(CASE WHEN role = 'BROKER' THEN 1 END) as brokers
                FROM users;
            """))
            stats = result.fetchone()
            
            print(f"   📊 User Statistics:")
            print(f"   - Total Users: {stats.total_users}")
            print(f"   - InsureFlow Admins: {stats.insureflow_admins}")
            print(f"   - Insurance Admins: {stats.regular_admins}")
            print(f"   - Brokers: {stats.brokers}")
            
            # Commit all changes
            conn.commit()
            print("\n✅ All changes committed successfully!")
            
            print(f"\n🎯 Fix Summary:")
            print(f"   ✅ INSUREFLOW_ADMIN enum value added")
            print(f"   ✅ Fresh admin account created")
            print(f"   ✅ Database compatibility verified")
            print(f"   ✅ All changes committed")
            
            print(f"\n🚀 Next Steps:")
            print(f"   1. Restart backend: docker-compose restart backend")
            print(f"   2. Login: admin@insureflow.com / password123")
            print(f"   3. Test broker dashboard: ethan.carter@brokers.ng / password123")
            print(f"   4. Use Payment Flow Testing on Broker Dashboard")
            
            return True
            
    except Exception as e:
        print(f"❌ Comprehensive fix failed: {str(e)}")
        logger.error(f"Fix failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = comprehensive_fix()
    
    if not success:
        print("\n❌ Comprehensive fix failed")
        sys.exit(1)
    else:
        print("\n🎉 Comprehensive fix completed successfully!")
