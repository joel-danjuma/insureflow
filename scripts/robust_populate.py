#!/usr/bin/env python3
"""
Robust database population script that handles SQLAlchemy compatibility issues.
Uses raw SQL queries to bypass ORM type mapping problems.
"""

import os
import sys
import logging
from datetime import datetime, date
from decimal import Decimal

# Add the app directory to the Python path
sys.path.append('/app')

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_database_url():
    """Get database URL from settings."""
    # Use the existing DATABASE_URL from settings which handles Docker service names correctly
    return settings.DATABASE_URL

def create_robust_engine():
    """Create a database engine with robust settings."""
    database_url = get_database_url()
    
    # Create engine with specific settings to avoid type issues
    engine = create_engine(
        database_url,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=False,
        # Disable SQLAlchemy's automatic type introspection that causes issues
        module=None
    )
    return engine

def check_table_exists(engine, table_name):
    """Check if a table exists in the database."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = :table_name
                );
            """), {"table_name": table_name})
            return result.scalar()
    except Exception as e:
        logger.error(f"Error checking table {table_name}: {e}")
        return False

def count_records(engine, table_name):
    """Count records in a table using raw SQL."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            return result.scalar()
    except Exception as e:
        logger.error(f"Error counting records in {table_name}: {e}")
        return 0

def populate_minimal_data(engine):
    """Populate minimal data using raw SQL to avoid ORM issues."""
    try:
        with engine.connect() as conn:
            # Start transaction
            trans = conn.begin()
            
            try:
                # Check if we have users
                user_count = conn.execute(text("SELECT COUNT(*) FROM users")).scalar()
                logger.info(f"Found {user_count} existing users")
                
                if user_count == 0:
                    logger.info("Creating minimal admin user...")
                    conn.execute(text("""
                        INSERT INTO users (
                            username, email, hashed_password, full_name, role, 
                            is_active, is_verified, created_at, updated_at
                        ) VALUES (
                            'admin', 'admin@insureflow.com', 
                            '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6hsxq5/H7S',
                            'System Administrator', 'ADMIN', 
                            true, true, NOW(), NOW()
                        ) ON CONFLICT (email) DO NOTHING
                    """))
                    logger.info("✅ Created admin user")

                    logger.info("Creating minimal broker user...")
                    conn.execute(text("""
                        INSERT INTO users (
                            username, email, hashed_password, full_name, role, 
                            is_active, is_verified, created_at, updated_at
                        ) VALUES (
                            'broker', 'broker@insureflow.com', 
                            '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6hsxq5/H7S',
                            'Test Broker', 'BROKER', 
                            true, true, NOW(), NOW()
                        ) ON CONFLICT (email) DO NOTHING
                    """))
                    logger.info("✅ Created broker user")
                
                # Check if we have insurance companies
                company_count = conn.execute(text("SELECT COUNT(*) FROM insurance_companies")).scalar()
                logger.info(f"Found {company_count} existing companies")
                
                if company_count == 0:
                    logger.info("Creating minimal insurance company...")
                    conn.execute(text("""
                        INSERT INTO insurance_companies (
                            name, email, phone_number, address, 
                            license_number, is_active, created_at, updated_at
                        ) VALUES (
                            'Test Insurance Company', 'admin@testinsurance.com',
                            '+234-800-000-0000', '123 Test Street, Lagos, Nigeria',
                            'INS-TEST-001', true, NOW(), NOW()
                        ) ON CONFLICT (license_number) DO NOTHING
                    """))
                    logger.info("✅ Created test insurance company")
                
                # Check if we have policies
                policy_count = conn.execute(text("SELECT COUNT(*) FROM policies")).scalar()
                logger.info(f"Found {policy_count} existing policies")
                
                if policy_count < 3:
                    logger.info("Creating minimal test policies...")
                    
                    # Get user and company IDs
                    user_result = conn.execute(text("SELECT id FROM users WHERE role = 'ADMIN' LIMIT 1"))
                    user_id = user_result.scalar()
                    
                    company_result = conn.execute(text("SELECT id FROM insurance_companies LIMIT 1"))
                    company_id = company_result.scalar()
                    
                    if user_id and company_id:
                        for i in range(1, 4):
                            conn.execute(text("""
                                INSERT INTO policies (
                                    policy_number, policy_type, user_id, company_id,
                                    coverage_amount, premium_amount, start_date, end_date,
                                    status, created_at, updated_at
                                ) VALUES (
                                    :policy_number, 'life', :user_id, :company_id,
                                    :coverage_amount, :premium_amount, :start_date, :end_date,
                                    'active', NOW(), NOW()
                                ) ON CONFLICT (policy_number) DO NOTHING
                            """), {
                                "policy_number": f"POL-TEST-{i:03d}",
                                "user_id": user_id,
                                "company_id": company_id,
                                "coverage_amount": Decimal("1000000.00"),
                                "premium_amount": Decimal("50000.00"),
                                "start_date": date.today(),
                                "end_date": date(2025, 12, 31)
                            })
                        logger.info("✅ Created test policies")
                
                # Check if we have premiums
                premium_count = conn.execute(text("SELECT COUNT(*) FROM premiums")).scalar()
                logger.info(f"Found {premium_count} existing premiums")
                
                if premium_count < 3:
                    logger.info("Creating minimal test premiums...")
                    
                    # Get policy IDs
                    policy_results = conn.execute(text("SELECT id FROM policies LIMIT 3"))
                    policy_ids = [row[0] for row in policy_results]
                    
                    for policy_id in policy_ids:
                        conn.execute(text("""
                            INSERT INTO premiums (
                                policy_id, amount, due_date, payment_status,
                                billing_period_start, billing_period_end,
                                grace_period_days, currency, created_at, updated_at
                            ) VALUES (
                                :policy_id, :amount, :due_date, 'PAID',
                                :billing_start, :billing_end,
                                30, 'NGN', NOW(), NOW()
                            ) ON CONFLICT DO NOTHING
                        """), {
                            "policy_id": policy_id,
                            "amount": Decimal("50000.00"),
                            "due_date": date(2024, 12, 31),
                            "billing_start": date(2024, 1, 1),
                            "billing_end": date(2024, 12, 31)
                        })
                    logger.info("✅ Created test premiums")
                
                # Commit transaction
                trans.commit()
                logger.info("✅ Database population completed successfully!")
                return True
                
            except Exception as e:
                trans.rollback()
                logger.error(f"Error during population, rolling back: {e}")
                return False
                
    except Exception as e:
        logger.error(f"Failed to populate database: {e}")
        return False

def main():
    """Main function to populate database."""
    logger.info("🚀 Starting robust database population...")
    
    try:
        # Create engine
        engine = create_robust_engine()
        logger.info("✅ Database engine created")
        
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✅ Database connection verified")
        
        # Check required tables exist
        required_tables = ['users', 'insurance_companies', 'policies', 'premiums']
        for table in required_tables:
            if not check_table_exists(engine, table):
                logger.error(f"❌ Required table '{table}' does not exist")
                return False
        logger.info("✅ All required tables exist")
        
        # Populate data
        success = populate_minimal_data(engine)
        
        if success:
            logger.info("🎉 Database population completed successfully!")
            return True
        else:
            logger.error("❌ Database population failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
