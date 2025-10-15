#!/usr/bin/env python3
"""
Fix user permissions for payment processing.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_user_permissions():
    """Update user permissions for payment processing."""
    
    try:
        # Create database engine
        engine = create_engine(settings.DATABASE_URL)
        
        with engine.connect() as conn:
            logger.info("🔧 Fixing user permissions for payment processing...")
            
            # Update all broker users to have payment permissions
            result = conn.execute(text("""
                UPDATE users 
                SET can_make_payments = true, can_create_policies = true
                WHERE role = 'BROKER'
            """))
            
            logger.info(f"✅ Updated {result.rowcount} broker users with payment permissions")
            
            # Update all admin users to have payment permissions
            result = conn.execute(text("""
                UPDATE users 
                SET can_make_payments = true, can_create_policies = true
                WHERE role = 'ADMIN'
            """))
            
            logger.info(f"✅ Updated {result.rowcount} admin users with payment permissions")
            
            # Update insurance admin users
            result = conn.execute(text("""
                UPDATE users 
                SET can_make_payments = true, can_create_policies = true
                WHERE role = 'INSURANCE_ADMIN'
            """))
            
            logger.info(f"✅ Updated {result.rowcount} insurance admin users with payment permissions")
            
            # Commit the changes
            conn.commit()
            
            logger.info("🎉 User permissions updated successfully!")
            
    except Exception as e:
        logger.error(f"❌ Error fixing user permissions: {e}")
        raise

if __name__ == "__main__":
    fix_user_permissions()
