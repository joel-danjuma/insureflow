#!/usr/bin/env python3
"""
Final fix for INSUREFLOW_ADMIN enum and account issues.
This script handles the SQLAlchemy ORM cache issue by using raw SQL.
"""

import sys
import os
from sqlalchemy import create_engine, text
import logging

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.core.security import get_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_enum_and_admin():
    """Fix the enum and admin account issues definitively."""
    
    try:
        # Create database engine
        engine = create_engine(settings.DATABASE_URL)
        
        with engine.connect() as conn:
            print("🔧 Final Fix for InsureFlow Admin Issues")
            print("=" * 50)
            
            # Step 1: Check current enum values
            print("📋 Checking current enum values...")
            result = conn.execute(text("""
                SELECT unnest(enum_range(NULL::userrole)) as enum_value;
            """))
            current_enums = [row[0] for row in result.fetchall()]
            print(f"   Current enum values: {current_enums}")
            
            # Step 2: Add INSUREFLOW_ADMIN if missing
            if 'INSUREFLOW_ADMIN' not in current_enums:
                print("➕ Adding INSUREFLOW_ADMIN to enum...")
                conn.execute(text("ALTER TYPE userrole ADD VALUE 'INSUREFLOW_ADMIN'"))
                print("✅ Enum value added")
            else:
                print("✅ INSUREFLOW_ADMIN already exists in enum")
            
            # Step 3: Check for existing admin users with INSUREFLOW_ADMIN role
            result = conn.execute(text("""
                SELECT id, email, role FROM users 
                WHERE role = 'INSUREFLOW_ADMIN' OR email = 'admin@insureflow.com'
            """))
            existing_admins = result.fetchall()
            
            if existing_admins:
                print("👤 Found existing admin users:")
                for admin in existing_admins:
                    print(f"   - ID: {admin.id}, Email: {admin.email}, Role: {admin.role}")
                
                # Update any admin@insureflow.com users to have correct role
                conn.execute(text("""
                    UPDATE users 
                    SET role = 'INSUREFLOW_ADMIN', updated_at = NOW()
                    WHERE email = 'admin@insureflow.com' AND role != 'INSUREFLOW_ADMIN'
                """))
                print("✅ Updated existing admin role")
            else:
                # Step 4: Create InsureFlow admin user
                print("👤 Creating InsureFlow admin user...")
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
                    ) ON CONFLICT (email) DO UPDATE SET
                        role = 'INSUREFLOW_ADMIN',
                        updated_at = NOW()
                """), {"hashed_password": hashed_password})
                print("✅ InsureFlow admin user created/updated")
            
            # Step 5: Verify the fix by checking the user
            result = conn.execute(text("""
                SELECT id, username, email, full_name, role, is_active 
                FROM users 
                WHERE email = 'admin@insureflow.com'
            """))
            admin_user = result.fetchone()
            
            if admin_user and admin_user.role == 'INSUREFLOW_ADMIN':
                print("\n🎉 InsureFlow Admin Account Verified:")
                print(f"   👤 Username: {admin_user.username}")
                print(f"   📧 Email: {admin_user.email}")
                print(f"   🏷️  Role: {admin_user.role}")
                print(f"   ✅ Active: {admin_user.is_active}")
                print(f"   🔑 Password: password123")
                
                # Step 6: Test enum compatibility by querying all users
                print("\n🧪 Testing enum compatibility...")
                result = conn.execute(text("SELECT COUNT(*) as count FROM users WHERE role = 'INSUREFLOW_ADMIN'"))
                admin_count = result.fetchone().count
                print(f"✅ Found {admin_count} INSUREFLOW_ADMIN user(s)")
                
                # Commit all changes
                conn.commit()
                print("\n✅ All fixes applied and committed successfully!")
                
                print(f"\n🚀 Next Steps:")
                print(f"   1. Restart your backend container: docker-compose restart backend")
                print(f"   2. Login with: admin@insureflow.com / password123")
                print(f"   3. Should now work without enum errors")
                
                return True
            else:
                print("❌ Failed to verify admin user creation")
                return False
                
    except Exception as e:
        print(f"❌ Error during fix: {str(e)}")
        logger.error(f"Fix failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = fix_enum_and_admin()
    
    if not success:
        print("\n❌ Fix failed - check the error messages above")
        sys.exit(1)
    else:
        print("\n🎯 Fix completed successfully!")
