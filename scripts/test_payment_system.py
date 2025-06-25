#!/usr/bin/env python3
"""
Comprehensive payment system testing script for InsureFlow.
Tests payment initiation, verification, and webhook handling.
"""
import asyncio
import sys
import os
from decimal import Decimal
from datetime import datetime

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.policy import Policy
from app.models.premium import Premium, PaymentStatus
from app.models.user import User
from app.models.broker import Broker
from app.services.payment_service import initiate_premium_payment
from app.services.squad_co import squad_co_service
from app.core.config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PaymentSystemTester:
    def __init__(self):
        self.db = SessionLocal()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()

    def test_squad_configuration(self):
        """Test Squad Co configuration and connectivity."""
        print("\n🔧 Testing Squad Co Configuration:")
        print(f"  - Base URL: {settings.SQUAD_BASE_URL}")
        print(f"  - Webhook URL: {settings.SQUAD_WEBHOOK_URL}")
        print(f"  - Secret Key Configured: {'✅' if settings.SQUAD_SECRET_KEY and settings.SQUAD_SECRET_KEY != '' else '❌'}")
        print(f"  - Public Key Configured: {'✅' if settings.SQUAD_PUBLIC_KEY and settings.SQUAD_PUBLIC_KEY != '' else '❌'}")
        
        if not settings.SQUAD_SECRET_KEY or settings.SQUAD_SECRET_KEY == "":
            print("❌ CRITICAL: Squad secret key not configured!")
            return False
        
        # Test service initialization
        service = squad_co_service
        print(f"  - Service Initialized: {'✅' if service.secret_key else '❌'}")
        
        return True

    def get_test_premium(self):
        """Get a test premium for payment testing."""
        print("\n🔍 Finding Test Premium:")
        
        # Find an unpaid premium
        unpaid_premium = self.db.query(Premium).filter(
            Premium.payment_status != PaymentStatus.PAID
        ).first()
        
        if not unpaid_premium:
            print("❌ No unpaid premiums found! Creating a test premium...")
            # Get any policy
            policy = self.db.query(Policy).first()
            if not policy:
                print("❌ No policies found in database!")
                return None
            
            # Create a test premium
            test_premium = Premium(
                policy_id=policy.id,
                amount=Decimal('50000.00'),  # ₦50,000 test amount
                currency="NGN",
                due_date=datetime.now().date(),
                payment_status=PaymentStatus.PENDING,
                premium_reference=f"TEST-PREM-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            )
            self.db.add(test_premium)
            self.db.commit()
            self.db.refresh(test_premium)
            unpaid_premium = test_premium
            print(f"✅ Created test premium: {test_premium.id}")
        
        # Get policy and user info
        policy = self.db.query(Policy).filter(Policy.id == unpaid_premium.policy_id).first()
        user = self.db.query(User).filter(User.id == policy.user_id).first() if policy else None
        broker = self.db.query(Broker).filter(Broker.id == policy.broker_id).first() if policy and policy.broker_id else None
        
        print(f"  - Premium ID: {unpaid_premium.id}")
        print(f"  - Amount: ₦{unpaid_premium.amount:,}")
        print(f"  - Status: {unpaid_premium.payment_status.value}")
        print(f"  - Policy: {policy.policy_number if policy else 'Unknown'}")
        print(f"  - Customer: {user.full_name if user else 'Unknown'} ({user.email if user else 'No email'})")
        print(f"  - Broker: {broker.name if broker else 'N/A'}")
        
        return unpaid_premium

    async def test_payment_initiation(self, premium):
        """Test payment initiation with Squad Co."""
        print(f"\n💳 Testing Payment Initiation for Premium {premium.id}:")
        
        try:
            result = await initiate_premium_payment(premium_id=premium.id, db=self.db)
            
            if "payment_url" in result:
                print("✅ Payment initiated successfully!")
                print(f"  - Payment URL: {result['payment_url']}")
                print(f"  - Transaction Ref: {result['transaction_ref']}")
                print(f"  - Message: {result['message']}")
                return result
            else:
                print(f"❌ Payment initiation failed: {result}")
                return None
                
        except Exception as e:
            print(f"❌ Payment error: {str(e)}")
            return None

    async def test_direct_squad_call(self):
        """Test direct Squad Co API call."""
        print(f"\n🌐 Testing Direct Squad Co API Call:")
        
        try:
            result = await squad_co_service.initiate_payment(
                amount=100.00,  # ₦100 test amount
                email="test@example.com",
                currency="NGN",
                metadata={"test": "direct_api_call", "timestamp": datetime.now().isoformat()}
            )
            
            if "error" in result:
                print(f"❌ Direct API call failed: {result['error']}")
                return False
            elif result.get("status") == 200:
                print("✅ Direct API call successful!")
                data = result.get("data", {})
                print(f"  - Transaction Ref: {data.get('transaction_ref', 'N/A')}")
                print(f"  - Checkout URL: {data.get('checkout_url', 'N/A')}")
                return True
            else:
                print(f"❌ Direct API call returned status: {result.get('status', 'Unknown')}")
                print(f"  - Message: {result.get('message', 'No message')}")
                return False
                
        except Exception as e:
            print(f"❌ Direct API call error: {str(e)}")
            return False

    def test_webhook_signature(self):
        """Test webhook signature verification."""
        print(f"\n🔒 Testing Webhook Signature Verification:")
        
        # Test data
        test_body = b'{"Event": "charge.success", "Body": {"transaction_ref": "test_ref"}}'
        
        # Generate a test signature (this would normally come from Squad)
        import hmac
        import hashlib
        
        if settings.SQUAD_SECRET_KEY:
            test_signature = hmac.new(
                settings.SQUAD_SECRET_KEY.encode('utf-8'),
                test_body,
                hashlib.sha512
            ).hexdigest()
            
            # Test verification
            is_valid = squad_co_service.verify_webhook_signature(test_body, test_signature)
            print(f"  - Signature Verification: {'✅' if is_valid else '❌'}")
            
            # Test with invalid signature
            is_invalid = squad_co_service.verify_webhook_signature(test_body, "invalid_signature")
            print(f"  - Invalid Signature Rejection: {'✅' if not is_invalid else '❌'}")
            
            return is_valid
        else:
            print("❌ Cannot test signature verification - no secret key")
            return False

    def get_payment_statistics(self):
        """Get payment system statistics."""
        print(f"\n📊 Payment System Statistics:")
        
        total_premiums = self.db.query(Premium).count()
        paid_premiums = self.db.query(Premium).filter(Premium.payment_status == PaymentStatus.PAID).count()
        pending_premiums = self.db.query(Premium).filter(Premium.payment_status == PaymentStatus.PENDING).count()
        overdue_premiums = self.db.query(Premium).filter(Premium.payment_status == PaymentStatus.OVERDUE).count()
        
        print(f"  - Total Premiums: {total_premiums}")
        if total_premiums > 0:
            print(f"  - Paid: {paid_premiums} ({(paid_premiums/total_premiums*100):.1f}%)")
            print(f"  - Pending: {pending_premiums} ({(pending_premiums/total_premiums*100):.1f}%)")
            print(f"  - Overdue: {overdue_premiums} ({(overdue_premiums/total_premiums*100):.1f}%)")
        else:
            print("  - No premium data to calculate statistics.")
        
        # Total amounts
        from sqlalchemy import func
        total_amount = self.db.query(func.sum(Premium.amount)).scalar() or Decimal('0')
        paid_amount = self.db.query(func.sum(Premium.paid_amount)).filter(
            Premium.payment_status == PaymentStatus.PAID
        ).scalar() or Decimal('0')
        
        print(f"  - Total Premium Amount: ₦{total_amount:,}")
        print(f"  - Total Paid Amount: ₦{paid_amount:,}")
        print(f"  - Outstanding Amount: ₦{(total_amount - paid_amount):,}")

async def main():
    """Main testing function."""
    print("🚀 InsureFlow Payment System Comprehensive Test")
    print("=" * 50)
    
    with PaymentSystemTester() as tester:
        # Test 1: Configuration
        config_ok = tester.test_squad_configuration()
        
        # Test 2: Statistics
        tester.get_payment_statistics()
        
        # Test 3: Webhook signature
        signature_ok = tester.test_webhook_signature()
        
        # Test 4: Direct API call (if config is OK)
        direct_api_ok = False
        if config_ok:
            direct_api_ok = await tester.test_direct_squad_call()
        
        # Test 5: Premium payment initiation
        payment_ok = False
        if config_ok:
            test_premium = tester.get_test_premium()
            if test_premium:
                payment_result = await tester.test_payment_initiation(test_premium)
                payment_ok = payment_result is not None
        
        # Summary
        print(f"\n📋 Test Summary:")
        print(f"  - Configuration: {'✅' if config_ok else '❌'}")
        print(f"  - Webhook Signature: {'✅' if signature_ok else '❌'}")
        print(f"  - Direct API Call: {'✅' if direct_api_ok else '❌'}")
        print(f"  - Payment Initiation: {'✅' if payment_ok else '❌'}")
        
        overall_status = "✅ PASS" if all([config_ok, signature_ok, direct_api_ok, payment_ok]) else "❌ FAIL"
        print(f"\n🎯 Overall Status: {overall_status}")
        
        if not all([config_ok, signature_ok, direct_api_ok, payment_ok]):
            print("\n💡 Troubleshooting Tips:")
            if not config_ok:
                print("  - Check your .env file for Squad Co configuration")
                print("  - Ensure SQUAD_SECRET_KEY is set to a valid value")
            if not direct_api_ok:
                print("  - Verify your Squad Co API credentials")
                print("  - Check if you're using sandbox vs production URLs")
                print("  - Ensure your internet connection is stable")
            if not payment_ok:
                print("  - Check database connectivity")
                print("  - Ensure test data exists in the database")
                print("  - Review application logs for detailed error messages")

if __name__ == "__main__":
    asyncio.run(main()) 