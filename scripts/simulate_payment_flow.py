import requests
import json
import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Configuration
# Since this runs inside the container, we can access the API at localhost:8000
API_BASE_URL = "http://localhost:8000/api/v1"
# Use the existing admin credentials or the test broker credentials
EMAIL = "admin@prestigeinsurance.ng" 
PASSWORD = "password123"

# Database connection for finding a valid premium
# Using the internal docker DNS if running inside container, or localhost if running on host
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://insureflow:password@localhost:5432/insureflow")

def get_db_session():
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

def login():
    print(f"🔑 Logging in as {EMAIL}...")
    url = f"{API_BASE_URL}/auth/login"
    payload = {
        "username": EMAIL,
        "password": PASSWORD
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    try:
        response = requests.post(url, data=payload, headers=headers)
        response.raise_for_status()
        token = response.json().get("access_token")
        print("✅ Login successful!")
        return token
    except requests.exceptions.RequestException as e:
        print(f"❌ Login failed: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response: {e.response.text}")
        sys.exit(1)

def find_valid_premium(db):
    print("🔍 Searching for an unpaid premium belonging to a user with a Virtual Account...")
    
    # Query to find a premium that is 'PENDING' or 'OVERDUE'
    # and belongs to a user who has a Virtual Account
    query = text("""
        SELECT 
            p.id as premium_id, 
            p.amount, 
            pol.policy_number, 
            u.email, 
            u.full_name,
            va.virtual_account_number,
            va.current_balance
        FROM premiums p
        JOIN policies pol ON p.policy_id = pol.id
        JOIN users u ON pol.user_id = u.id
        JOIN virtual_accounts va ON u.id = va.user_id
        WHERE p.payment_status IN ('PENDING', 'OVERDUE')
        LIMIT 1;
    """)
    
    result = db.execute(query).fetchone()
    
    if result:
        print(f"✅ Found Premium ID: {result.premium_id}")
        print(f"   Amount: ₦{result.amount}")
        print(f"   User: {result.full_name} ({result.email})")
        print(f"   Virtual Account: {result.virtual_account_number}")
        print(f"   Current VA Balance: ₦{result.current_balance}")
        return result.premium_id
    else:
        print("❌ No suitable premium found. Ensure users with VAs have unpaid premiums.")
        return None

def simulate_payment(token, premium_id):
    print(f"🚀 Initiating payment simulation for Premium ID {premium_id}...")
    url = f"{API_BASE_URL}/testing/simulate-payment"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "premium_id": premium_id
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        print("\n✅ Payment Simulation Successful!")
        print("-" * 50)
        print(json.dumps(data, indent=2))
        print("-" * 50)
        print("👉 The premium status should now be 'PAID'.")
        print("👉 A transaction record should appear on the Insurance Firm Dashboard.")
        print("👉 The Virtual Account balance should have decreased.")
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Payment Simulation Failed: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response: {e.response.text}")

def main():
    db = get_db_session()
    try:
        premium_id = find_valid_premium(db)
        if premium_id:
            token = login()
            simulate_payment(token, premium_id)
    finally:
        db.close()

if __name__ == "__main__":
    main()

