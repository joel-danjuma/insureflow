#!/usr/bin/env python3
"""
Simple database population script that avoids SQLAlchemy compatibility issues.
Creates minimal data needed for broker dashboard to work.
"""

import os
import sys
from datetime import datetime, date, timedelta
from decimal import Decimal
import random

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import SessionLocal
from app.core.security import get_password_hash

def main():
    """Create minimal data using raw SQL to avoid SQLAlchemy type issues."""
    print("🚀 Starting simple database population...")
    
    db = SessionLocal()
    
    try:
        # Check if we already have policies
        result = db.execute(text("SELECT COUNT(*) FROM policies")).fetchone()
        policy_count = result[0] if result else 0
        
        if policy_count > 0:
            print(f"ℹ️  Database already has {policy_count} policies")
            return
        
        print("✅ Creating minimal test data using raw SQL...")
        
        # Create insurance company if not exists
        db.execute(text("""
            INSERT INTO insurance_companies (name, registration_number, address, contact_email, contact_phone, website, description, created_at, updated_at)
            SELECT 'Secure Life Insurance Nigeria', 'RC123456', '14B Adeola Odeku Street, Victoria Island, Lagos', 'info@securelife.ng', '+234-1-234-5678', 'https://securelife.ng', 'Leading life insurance provider in Nigeria', NOW(), NOW()
            WHERE NOT EXISTS (SELECT 1 FROM insurance_companies WHERE name = 'Secure Life Insurance Nigeria')
        """))
        
        # Get company ID
        company_result = db.execute(text("SELECT id FROM insurance_companies WHERE name = 'Secure Life Insurance Nigeria' LIMIT 1")).fetchone()
        company_id = company_result[0] if company_result else 1
        
        # Create users using raw SQL to avoid enum issues
        hashed_password = get_password_hash('password123')
        
        # Create Sarah Johnson (Insurance Admin)
        db.execute(text("""
            INSERT INTO users (username, email, hashed_password, full_name, role, is_active, is_verified, created_at, updated_at)
            SELECT 'sarah.johnson', 'sarah.johnson@sovereigntrust.com', :password, 'Sarah Johnson', 'INSURANCE_ADMIN', true, true, NOW(), NOW()
            WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = 'sarah.johnson@sovereigntrust.com')
        """), {"password": hashed_password})
        
        # Create John Broker
        db.execute(text("""
            INSERT INTO users (username, email, hashed_password, full_name, role, is_active, is_verified, created_at, updated_at)
            SELECT 'john.broker', 'john.broker@scib.ng', :password, 'John Broker', 'BROKER', true, true, NOW(), NOW()
            WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = 'john.broker@scib.ng')
        """), {"password": hashed_password})
        
        # Get John's user ID
        john_result = db.execute(text("SELECT id FROM users WHERE email = 'john.broker@scib.ng' LIMIT 1")).fetchone()
        john_id = john_result[0] if john_result else None
        
        if john_id:
            # Create broker profile
            db.execute(text("""
                INSERT INTO brokers (user_id, name, license_number, agency_name, contact_email, contact_phone, office_address, commission_type, default_commission_rate, total_policies_sold, total_premiums_collected, total_commission_earned, is_active, is_verified, created_at, updated_at)
                SELECT :user_id, 'SCIB', 'BRK-2023-001', 'Sovereign Capital Investment Banking', 'john.broker@scib.ng', '+234-801-234-5678', 'Lagos, Nigeria', 'percentage', 0.125, 0, 0, 0, true, true, NOW(), NOW()
                WHERE NOT EXISTS (SELECT 1 FROM brokers WHERE user_id = :user_id)
            """), {"user_id": john_id})
            
            # Get broker ID
            broker_result = db.execute(text("SELECT id FROM brokers WHERE user_id = :user_id LIMIT 1"), {"user_id": john_id}).fetchone()
            broker_id = broker_result[0] if broker_result else None
        else:
            broker_id = None
        
        # Create customer users
        for i in range(5):
            email = f'customer{i+1}@example.com'
            db.execute(text("""
                INSERT INTO users (username, email, hashed_password, full_name, role, is_active, is_verified, created_at, updated_at)
                SELECT :username, :email, :password, :full_name, 'CUSTOMER', true, true, NOW(), NOW()
                WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = :email)
            """), {
                "username": f'customer{i+1}',
                "email": email,
                "password": hashed_password,
                "full_name": f'Customer {i+1}'
            })
        
        # Get customer IDs
        customer_results = db.execute(text("SELECT id FROM users WHERE role = 'CUSTOMER' LIMIT 5")).fetchall()
        customer_ids = [row[0] for row in customer_results]
        
        # Create policies using raw SQL
        policy_types = ['LIFE', 'AUTO', 'HEALTH']
        
        for i in range(8):
            policy_number = f'POL-001-2024-{i+1:04d}'
            customer_id = random.choice(customer_ids) if customer_ids else john_id
            policy_type = random.choice(policy_types)
            
            # Generate realistic amounts
            if policy_type == 'LIFE':
                premium_amount = random.randint(200000, 800000)
                coverage_amount = random.randint(5000000, 20000000)
            elif policy_type == 'AUTO':
                premium_amount = random.randint(150000, 600000)
                coverage_amount = random.randint(2000000, 10000000)
            else:  # HEALTH
                premium_amount = random.randint(100000, 400000)
                coverage_amount = random.randint(1000000, 5000000)
            
            start_date = date.today() - timedelta(days=random.randint(30, 300))
            end_date = start_date + timedelta(days=365)
            
            # Insert policy
            db.execute(text("""
                INSERT INTO policies (
                    policy_number, policy_type, user_id, company_id, broker_id, 
                    status, start_date, end_date, premium_amount, coverage_amount,
                    company_name, contact_person, contact_email, contact_phone,
                    created_at, updated_at
                ) VALUES (
                    :policy_number, :policy_type, :user_id, :company_id, :broker_id,
                    'ACTIVE', :start_date, :end_date, :premium_amount, :coverage_amount,
                    :company_name, :contact_person, :contact_email, :contact_phone,
                    NOW(), NOW()
                )
            """), {
                "policy_number": policy_number,
                "policy_type": policy_type,
                "user_id": customer_id,
                "company_id": company_id,
                "broker_id": broker_id,
                "start_date": start_date,
                "end_date": end_date,
                "premium_amount": premium_amount,
                "coverage_amount": coverage_amount,
                "company_name": f'Company {i+1}',
                "contact_person": f'Customer {i+1}',
                "contact_email": f'customer{i+1}@example.com',
                "contact_phone": '+234-800-000-0000'
            })
        
        # Get policy IDs
        policy_results = db.execute(text("SELECT id, premium_amount, start_date FROM policies")).fetchall()
        
        # Create premiums
        premiums_created = 0
        for policy_id, premium_amount, start_date in policy_results:
            # Create 2-3 premiums per policy
            for j in range(random.randint(2, 3)):
                due_date = start_date + timedelta(days=j*30)
                status = 'PAID' if due_date <= date.today() and random.random() > 0.3 else 'PENDING'
                
                db.execute(text("""
                    INSERT INTO premiums (policy_id, amount, due_date, payment_status, billing_cycle, currency, created_at, updated_at)
                    VALUES (:policy_id, :amount, :due_date, :payment_status, 'monthly', 'NGN', NOW(), NOW())
                """), {
                    "policy_id": policy_id,
                    "amount": float(premium_amount),
                    "due_date": due_date,
                    "payment_status": status.lower()  # Convert to lowercase for enum
                })
                premiums_created += 1
        
        db.commit()
        
        print(f'✅ Created {len(policy_results)} policies')
        print(f'✅ Created {premiums_created} premiums')
        print(f'✅ Simple test data created successfully!')
        
    except Exception as e:
        print(f"❌ Error during simple population: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()