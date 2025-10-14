#!/usr/bin/env python3
"""
Fix InsureFlow Admin account creation.
Adds INSUREFLOW_ADMIN to userrole enum and creates the admin account.
"""

import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.core.security import get_password_hash

def fix_insureflow_admin():
    """Fix the InsureFlow admin account and enum issues."""
    
    try:
        # Create database engine
        engine = create_engine(settings.DATABASE_URL)
        
        with engine.connect() as conn:
            # Start transaction
            trans = conn.begin()
            
            try:
                print("🔧 Fixing InsureFlow Admin Account...")
                
                # Step 1: Add INSUREFLOW_ADMIN to enum if it doesn't exist
                print("📋 Adding INSUREFLOW_ADMIN to userrole enum...")
                conn.execute(text("ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'INSUREFLOW_ADMIN'"))
                print("✅ Enum updated successfully")
                
                # Step 2: Check if InsureFlow admin already exists
                result = conn.execute(text("""
                    SELECT id, email, role FROM users 
                    WHERE email = 'admin@insureflow.com' OR role = 'INSUREFLOW_ADMIN'
                """))
                existing_admin = result.fetchone()
                
                if existing_admin:
                    print(f"ℹ️  Found existing admin: {existing_admin.email} (Role: {existing_admin.role})")
                    
                    # Update role if it's wrong
                    if existing_admin.role != 'INSUREFLOW_ADMIN':
                        print("🔄 Updating admin role to INSUREFLOW_ADMIN...")
                        conn.execute(text("""
                            UPDATE users 
                            SET role = 'INSUREFLOW_ADMIN', updated_at = NOW()
                            WHERE id = :user_id
                        """), {"user_id": existing_admin.id})
                        print("✅ Admin role updated")
                else:
                    # Step 3: Create InsureFlow admin user
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
                        )
                    """), {"hashed_password": hashed_password})
                    print("✅ InsureFlow admin user created")
                
                # Step 4: Verify the fix
                result = conn.execute(text("""
                    SELECT username, email, full_name, role, is_active 
                    FROM users 
                    WHERE email = 'admin@insureflow.com'
                """))
                admin_user = result.fetchone()
                
                if admin_user:
                    print("\n🎉 InsureFlow Admin Account Details:")
                    print(f"   👤 Username: {admin_user.username}")
                    print(f"   📧 Email: {admin_user.email}")
                    print(f"   🏷️  Role: {admin_user.role}")
                    print(f"   ✅ Active: {admin_user.is_active}")
                    print(f"   🔑 Password: password123")
                    
                    print(f"\n🚀 Admin can now access:")
                    print(f"   📊 InsureFlow Admin Dashboard")
                    print(f"   📋 Platform-wide transaction logs")
                    print(f"   💰 Commission analytics")
                    print(f"   🔧 System health monitoring")
                else:
                    print("❌ Failed to verify admin user creation")
                    return False
                
                # Commit transaction
                trans.commit()
                print("\n✅ All fixes applied successfully!")
                return True
                
            except Exception as e:
                trans.rollback()
                print(f"❌ Error during fix: {str(e)}")
                return False
                
    except Exception as e:
        print(f"❌ Database connection error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 InsureFlow Admin Account Fix")
    print("=" * 40)
    
    success = fix_insureflow_admin()
    
    if success:
        print("\n🎯 Next Steps:")
        print("   1. Restart your backend container")
        print("   2. Login with: admin@insureflow.com / password123")
        print("   3. Access the InsureFlow Admin Dashboard")
        print("   4. Test payment flow from Broker Dashboard")
    else:
        print("\n❌ Fix failed - check the error messages above")
        sys.exit(1)
