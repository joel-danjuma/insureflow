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

def prepare_data(db):
    print("🔍 Searching for a suitable premium and fixing Virtual Account linkage...")
    
    # Find a premium AND the associated user's virtual account
    query = text("""
        SELECT 
            p.id as premium_id, 
            p.amount, 
            pol.id as policy_id,
            pol.policy_number, 
            u.id as user_id,
            u.full_name,
            va.id as va_id,
            va.virtual_account_number,
            va.policy_id as va_policy_id
        FROM premiums p
        JOIN policies pol ON p.policy_id = pol.id
        JOIN users u ON pol.user_id = u.id
        JOIN virtual_accounts va ON u.id = va.user_id
        WHERE p.payment_status IN ('PENDING', 'OVERDUE')
        LIMIT 1;
    """)
    
    result = db.execute(query).fetchone()
    
    if not result:
        print("❌ No suitable premium found. Ensure users with VAs have unpaid premiums.")
        return None

    print(f"✅ Found Premium ID: {result.premium_id} (Policy ID: {result.policy_id})")
    print(f"   User: {result.full_name}")
    print(f"   Virtual Account: {result.virtual_account_number}")

    # CRITICAL FIX: Ensure the Virtual Account is linked to this Policy
    # The webhook handler relies on va.policy_id to find the premiums to pay
    if result.va_policy_id != result.policy_id:
        print(f"⚠️  VA Policy ID ({result.va_policy_id}) matches mismatch Premium Policy ID ({result.policy_id}). Fixing...")
        update_query = text("UPDATE virtual_accounts SET policy_id = :pid WHERE id = :va_id")
        db.execute(update_query, {"pid": result.policy_id, "va_id": result.va_id})
        db.commit()
        print(f"✅ Virtual Account {result.virtual_account_number} linked to Policy {result.policy_id}")
    else:
        print("✅ Virtual Account is correctly linked to the Policy.")

    return result.premium_id

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
        print(json.dumps(data, indent=2))
        print("\n👉 CHECK DASHBOARD NOW: The 'Latest Payments' section should be updated.")
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Payment Simulation Failed: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response: {e.response.text}")

def main():
    db = get_db_session()
    try:
        premium_id = prepare_data(db)
        if premium_id:
            token = login()
            simulate_payment(token, premium_id)
    finally:
        db.close()

if __name__ == "__main__":
    main()

