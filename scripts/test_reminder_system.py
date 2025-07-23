#!/usr/bin/env python3
"""
Test script for the payment reminder system in InsureFlow.
"""
import sys
import os
from datetime import datetime, date, timedelta
from decimal import Decimal

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.policy import Policy, PolicyStatus
from app.models.premium import Premium, PaymentStatus
from app.models.user import User, UserRole
from app.models.broker import Broker
from app.crud import policy as crud_policy
from app.crud import premium as crud_premium
import requests
import json

class ReminderSystemTester:
    def __init__(self):
        self.db = SessionLocal()
        self.base_url = "http://localhost:8000/api/v1"
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()

    def get_outstanding_policies(self):
        """Find policies with outstanding premiums that need reminders."""
        print("\n🔍 Finding Outstanding Policies:")
        
        outstanding_policies = []
        
        # Get policies with unpaid premiums
        policies_with_unpaid = self.db.query(Policy).join(Premium).filter(
            Premium.payment_status.in_([PaymentStatus.PENDING, PaymentStatus.OVERDUE]),
            Policy.status == PolicyStatus.ACTIVE
        ).distinct().all()
        
        for policy in policies_with_unpaid:
            unpaid_premiums = self.db.query(Premium).filter(
                Premium.policy_id == policy.id,
                Premium.payment_status.in_([PaymentStatus.PENDING, PaymentStatus.OVERDUE])
            ).all()
            
            if unpaid_premiums:
                total_outstanding = sum(p.outstanding_amount for p in unpaid_premiums)
                
                outstanding_policies.append({
                    "policy": policy,
                    "unpaid_count": len(unpaid_premiums),
                    "total_outstanding": total_outstanding,
                    "oldest_due_date": min(p.due_date for p in unpaid_premiums),
                    "broker_name": policy.broker.name if policy.broker else "N/A"
                })
        
        # Sort by oldest due date (most overdue first)
        outstanding_policies.sort(key=lambda x: x["oldest_due_date"])
        
        print(f"  - Found {len(outstanding_policies)} policies with outstanding premiums")
        
        for i, data in enumerate(outstanding_policies[:5]):  # Show top 5
            policy = data["policy"]
            days_overdue = (date.today() - data["oldest_due_date"]).days
            status = "OVERDUE" if days_overdue > 0 else "DUE SOON"
            
            print(f"    {i+1}. Policy {policy.policy_number} - {data['broker_name']}")
            print(f"       Outstanding: ₦{data['total_outstanding']:,} ({data['unpaid_count']} premiums)")
            print(f"       Status: {status} ({abs(days_overdue)} days)")
        
        return outstanding_policies

def main():
    """Main testing function."""
    print("🚀 InsureFlow Payment Reminder System Test")
    print("=" * 50)
    
    with ReminderSystemTester() as tester:
        # Test 1: Get outstanding policies
        outstanding_policies = tester.get_outstanding_policies()
        
        if not outstanding_policies:
            print("⚠️  No outstanding policies found - reminder system has nothing to test")
            return
        
        print(f"\n🎯 Found {len(outstanding_policies)} policies that need reminders!")

if __name__ == "__main__":
    main()
