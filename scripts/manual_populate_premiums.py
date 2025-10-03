#!/usr/bin/env python3
"""
Manual script to populate premiums data for existing policies.
This ensures the broker dashboard has data to display.
"""

import os
import sys
from datetime import datetime, date, timedelta

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import SessionLocal

def main():
    """Manually populate premiums for existing policies."""
    print("🚀 Starting manual premium population...")
    
    db = SessionLocal()
    
    try:
        # Check existing policies
        policies_result = db.execute(text("SELECT id, policy_number, premium_amount FROM policies ORDER BY id")).fetchall()
        
        if not policies_result:
            print("❌ No policies found! Cannot create premiums.")
            return
        
        print(f"📋 Found {len(policies_result)} policies")
        
        # Check existing premiums
        premiums_result = db.execute(text("SELECT COUNT(*) as count FROM premiums")).fetchone()
        existing_premiums = premiums_result[0] if premiums_result else 0
        
        if existing_premiums > 0:
            print(f"ℹ️  Database already has {existing_premiums} premiums")
            return
        
        print("✅ Creating premiums for existing policies...")
        
        premiums_created = 0
        
        for policy_id, policy_number, premium_amount in policies_result:
            print(f"📋 Creating premiums for policy {policy_number} (₦{premium_amount:,.2f})")
            
            # Create 2 premiums per policy - one paid, one pending
            premium_data = [
                {
                    'due_date': date.today() - timedelta(days=60),
                    'status': 'PAID',
                    'paid_amount': float(premium_amount)
                },
                {
                    'due_date': date.today() + timedelta(days=30),
                    'status': 'PENDING', 
                    'paid_amount': 0
                }
            ]
            
            for i, data in enumerate(premium_data):
                try:
                    db.execute(text("""
                        INSERT INTO premiums (
                            policy_id, amount, due_date, payment_status, billing_cycle, 
                            currency, grace_period_days, paid_amount, late_fee_amount, 
                            created_at, updated_at
                        ) VALUES (
                            :policy_id, :amount, :due_date, :payment_status, 'MONTHLY',
                            'NGN', 30, :paid_amount, 0,
                            NOW(), NOW()
                        )
                    """), {
                        'policy_id': policy_id,
                        'amount': float(premium_amount),
                        'due_date': data['due_date'],
                        'payment_status': data['status'],
                        'paid_amount': data['paid_amount']
                    })
                    premiums_created += 1
                    print(f"  ✅ Created premium {i+1}: {data['status']} - Due {data['due_date']}")
                    
                except Exception as e:
                    print(f"  ❌ Error creating premium {i+1}: {e}")
        
        db.commit()
        
        # Verify creation
        final_count = db.execute(text("SELECT COUNT(*) as count FROM premiums")).fetchone()
        final_premiums = final_count[0] if final_count else 0
        
        print(f"✅ Successfully created {premiums_created} premiums")
        print(f"📊 Total premiums in database: {final_premiums}")
        
        # Calculate totals for verification
        totals_result = db.execute(text("""
            SELECT 
                COUNT(*) as total_premiums,
                SUM(amount) as total_amount,
                SUM(CASE WHEN payment_status = 'PAID' THEN amount ELSE 0 END) as paid_amount,
                SUM(CASE WHEN payment_status = 'PENDING' THEN amount ELSE 0 END) as pending_amount
            FROM premiums
        """)).fetchone()
        
        if totals_result:
            total_premiums, total_amount, paid_amount, pending_amount = totals_result
            print(f"📊 Premium Summary:")
            print(f"   Total Premiums: {total_premiums}")
            print(f"   Total Amount: ₦{total_amount:,.2f}")
            print(f"   Paid Amount: ₦{paid_amount:,.2f}")
            print(f"   Pending Amount: ₦{pending_amount:,.2f}")
            print(f"   Expected Commission (15%): ₦{float(total_amount) * 0.15:,.2f}")
        
    except Exception as e:
        print(f"❌ Error during manual population: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
