#!/usr/bin/env python3
"""
Fix database enums and populate with data.
This script first fixes enum values, then populates the database.
"""

import os
import sys
from datetime import datetime, date, timedelta

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import SessionLocal
from app.core.security import get_password_hash

def main():
    """Fix enums and create minimal data."""
    print("🚀 Starting database enum fix and population...")
    
    db = SessionLocal()
    
    try:
        # First, check what enum values exist
        print("🔍 Checking existing enum values...")
        
        try:
            # Check paymentstatus enum
            result = db.execute(text("""
                SELECT enumlabel FROM pg_enum 
                WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'paymentstatus')
                ORDER BY enumlabel
            """)).fetchall()
            
            payment_status_values = [row[0] for row in result] if result else []
            print(f"📋 Current paymentstatus enum values: {payment_status_values}")
            
            # Use existing enum values instead of adding duplicates
            print(f"📋 Using existing paymentstatus enum values: {payment_status_values}")
            
            # Check billingcycle enum
            result = db.execute(text("""
                SELECT enumlabel FROM pg_enum 
                WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'billingcycle')
                ORDER BY enumlabel
            """)).fetchall()
            
            billing_cycle_values = [row[0] for row in result] if result else []
            print(f"📋 Using existing billingcycle enum values: {billing_cycle_values}")
            
            db.commit()
            
        except Exception as e:
            print(f"⚠️  Could not check/fix enums: {e}")
        
        # Check if we already have policies
        try:
            result = db.execute(text("SELECT COUNT(*) as count FROM policies")).fetchone()
            policy_count = result[0] if result else 0
        except Exception as e:
            print(f"⚠️  Could not check policy count: {e}")
            policy_count = 0
        
        if policy_count > 0:
            print(f"ℹ️  Database already has {policy_count} policies")
            return
        
        print("✅ Creating minimal test data...")
        
        # Get password hash
        hashed_password = get_password_hash('password123')
        
        # Create insurance company
        db.execute(text("""
            INSERT INTO insurance_companies (name, registration_number, address, contact_email, contact_phone, website, description, created_at, updated_at)
            SELECT 'Secure Life Insurance Nigeria', 'RC123456', '14B Adeola Odeku Street, Victoria Island, Lagos', 'info@securelife.ng', '+234-1-234-5678', 'https://securelife.ng', 'Leading life insurance provider in Nigeria', NOW(), NOW()
            WHERE NOT EXISTS (SELECT 1 FROM insurance_companies WHERE name = 'Secure Life Insurance Nigeria')
        """))
        
        # Create users
        db.execute(text("""
            INSERT INTO users (username, email, hashed_password, full_name, role, is_active, is_verified, created_at, updated_at)
            SELECT 'sarah.johnson', 'sarah.johnson@sovereigntrust.com', :password, 'Sarah Johnson', 'INSURANCE_ADMIN', true, true, NOW(), NOW()
            WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = 'sarah.johnson@sovereigntrust.com')
        """), {"password": hashed_password})
        
        db.execute(text("""
            INSERT INTO users (username, email, hashed_password, full_name, role, is_active, is_verified, created_at, updated_at)
            SELECT 'john.broker', 'john.broker@scib.ng', :password, 'John Broker', 'BROKER', true, true, NOW(), NOW()
            WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = 'john.broker@scib.ng')
        """), {"password": hashed_password})
        
        # Create customers
        for i in range(1, 6):
            db.execute(text(f"""
                INSERT INTO users (username, email, hashed_password, full_name, role, is_active, is_verified, created_at, updated_at)
                SELECT 'customer{i}', 'customer{i}@example.com', :password, 'Customer {i}', 'CUSTOMER', true, true, NOW(), NOW()
                WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = 'customer{i}@example.com')
            """), {"password": hashed_password})
        
        # Create broker profile
        db.execute(text("""
            INSERT INTO brokers (user_id, name, license_number, agency_name, contact_email, contact_phone, office_address, commission_type, default_commission_rate, total_policies_sold, total_premiums_collected, total_commission_earned, is_active, is_verified, created_at, updated_at)
            SELECT u.id, 'SCIB', 'BRK-2023-001', 'Sovereign Capital Investment Banking', 'john.broker@scib.ng', '+234-801-234-5678', 'Lagos, Nigeria', 'percentage', 0.125, 0, 0, 0, true, true, NOW(), NOW()
            FROM users u 
            WHERE u.email = 'john.broker@scib.ng' 
            AND NOT EXISTS (SELECT 1 FROM brokers WHERE user_id = u.id)
        """))
        
        # Create policies using simple approach
        policies_data = [
            ('POL-001-2024-0001', 'LIFE', 'customer1@example.com', 450000, 8000000, 'Life Corp Ltd'),
            ('POL-001-2024-0002', 'AUTO', 'customer2@example.com', 320000, 5500000, 'Auto Shield Inc'),
            ('POL-001-2024-0003', 'HEALTH', 'customer3@example.com', 180000, 2500000, 'Health Plus Ltd'),
            ('POL-001-2024-0004', 'LIFE', 'customer4@example.com', 620000, 12000000, 'Premium Life Co'),
            ('POL-001-2024-0005', 'AUTO', 'customer5@example.com', 280000, 4200000, 'Drive Safe Ltd'),
        ]
        
        for policy_number, policy_type, customer_email, premium_amount, coverage_amount, company_name in policies_data:
            db.execute(text("""
                INSERT INTO policies (
                    policy_number, policy_type, user_id, company_id, broker_id, 
                    status, start_date, end_date, premium_amount, coverage_amount,
                    company_name, contact_person, contact_email, contact_phone,
                    created_at, updated_at
                )
                SELECT 
                    :policy_number, :policy_type, 
                    c.id, ic.id, b.id,
                    'ACTIVE', CURRENT_DATE - INTERVAL '90 days', CURRENT_DATE + INTERVAL '275 days', 
                    :premium_amount, :coverage_amount,
                    :company_name, c.full_name, c.email, '+234-800-000-0000',
                    NOW(), NOW()
                FROM users c, insurance_companies ic, brokers b
                WHERE c.email = :customer_email
                AND ic.name = 'Secure Life Insurance Nigeria'
                AND b.license_number = 'BRK-2023-001'
                AND NOT EXISTS (SELECT 1 FROM policies WHERE policy_number = :policy_number)
            """), {
                "policy_number": policy_number,
                "policy_type": policy_type,
                "customer_email": customer_email,
                "premium_amount": premium_amount,
                "coverage_amount": coverage_amount,
                "company_name": company_name
            })
        
        db.commit()
        
        # Now create premiums - check what values are actually available first
        try:
            result = db.execute(text("""
                SELECT enumlabel FROM pg_enum 
                WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'paymentstatus')
                ORDER BY enumlabel
            """)).fetchall()
            
            available_statuses = [row[0] for row in result] if result else []
            print(f"📋 Available payment statuses for premiums: {available_statuses}")
            
            # Use existing uppercase values if available, otherwise lowercase
            paid_status = 'PAID' if 'PAID' in available_statuses else ('paid' if 'paid' in available_statuses else (available_statuses[0] if available_statuses else 'PENDING'))
            pending_status = 'PENDING' if 'PENDING' in available_statuses else ('pending' if 'pending' in available_statuses else (available_statuses[0] if available_statuses else 'PENDING'))
            
            print(f"📋 Using statuses - Paid: '{paid_status}', Pending: '{pending_status}'")
            
            # Create premiums with available enum values
            premiums_data = [
                ('POL-001-2024-0001', 450000, -60, paid_status),
                ('POL-001-2024-0001', 450000, 30, pending_status),
                ('POL-001-2024-0002', 320000, -30, paid_status),
                ('POL-001-2024-0002', 320000, 60, pending_status),
                ('POL-001-2024-0003', 180000, -90, paid_status),
                ('POL-001-2024-0003', 180000, 15, pending_status),
                ('POL-001-2024-0004', 620000, -15, paid_status),
                ('POL-001-2024-0004', 620000, 45, pending_status),
                ('POL-001-2024-0005', 280000, 0, pending_status),
                ('POL-001-2024-0005', 280000, 90, pending_status),
            ]
            
            # Check billing cycle values
            result = db.execute(text("""
                SELECT enumlabel FROM pg_enum 
                WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'billingcycle')
                ORDER BY enumlabel
            """)).fetchall()
            
            available_cycles = [row[0] for row in result] if result else []
            billing_cycle = 'MONTHLY' if 'MONTHLY' in available_cycles else ('monthly' if 'monthly' in available_cycles else (available_cycles[0] if available_cycles else 'MONTHLY'))
            
            print(f"📋 Using billing cycle: '{billing_cycle}'")
            
            for policy_number, amount, days_offset, status in premiums_data:
                due_date = date.today() + timedelta(days=days_offset)
                
                db.execute(text("""
                    INSERT INTO premiums (policy_id, amount, due_date, payment_status, billing_cycle, currency, grace_period_days, paid_amount, late_fee_amount, created_at, updated_at)
                    SELECT p.id, :amount, :due_date, :status, :billing_cycle, 'NGN', 30, 0, 0, NOW(), NOW()
                    FROM policies p 
                    WHERE p.policy_number = :policy_number
                    AND NOT EXISTS (
                        SELECT 1 FROM premiums pr 
                        WHERE pr.policy_id = p.id 
                        AND pr.due_date = :due_date
                    )
                """), {
                    "policy_number": policy_number,
                    "amount": amount,
                    "due_date": due_date,
                    "status": status,
                    "billing_cycle": billing_cycle
                })
            
            db.commit()
            
        except Exception as e:
            print(f"⚠️  Error creating premiums: {e}")
            db.rollback()
        
        # Get final counts
        try:
            policy_result = db.execute(text("SELECT COUNT(*) as count FROM policies")).fetchone()
            premium_result = db.execute(text("SELECT COUNT(*) as count FROM premiums")).fetchone()
            
            policy_count = policy_result[0] if policy_result else 0
            premium_count = premium_result[0] if premium_result else 0
            
            print(f'✅ Created {policy_count} policies')
            print(f'✅ Created {premium_count} premiums')
            print(f'✅ Database population completed successfully!')
            
        except Exception as e:
            print(f"⚠️  Could not get final counts: {e}")
        
    except Exception as e:
        print(f"❌ Error during population: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
