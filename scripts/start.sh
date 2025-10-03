#!/bin/bash
set -e

echo "🚀 Starting InsureFlow Backend..."

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
python3 << 'END'
import time
import sys
from sqlalchemy import create_engine, text
from app.core.config import settings

max_retries = 30
for i in range(max_retries):
    try:
        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Database is ready!")
        sys.exit(0)
    except Exception as e:
        if i < max_retries - 1:
            print(f"⏳ Waiting for database... ({i+1}/{max_retries})")
            time.sleep(2)
        else:
            print(f"❌ Database not ready: {e}")
            sys.exit(1)
END

# Run database migrations
echo "📋 Running database migrations..."
alembic upgrade head

# Populate database with comprehensive demo data if empty (optional - don't fail if it errors)
echo "👥 Checking and populating database..."
python3 scripts/populate_database.py || {
    echo "⚠️  Database population failed (model/schema mismatch)"
    echo "⚠️  Trying simple population script..."
    python3 scripts/simple_populate.py || {
        echo "⚠️  Simple population also failed, trying direct SQL approach..."
    python3 scripts/direct_sql_populate.py || {
        echo "⚠️  Direct SQL population also failed, trying raw SQL approach..."
        
        # Check if we have policies first
        POLICY_COUNT=$(python3 -c "
from app.core.database import get_db
from sqlalchemy import text
try:
    db = next(get_db())
    result = db.execute(text('SELECT COUNT(*) FROM policies')).fetchone()
    print(result[0] if result else 0)
    db.close()
except:
    print(0)
" 2>/dev/null || echo 0)
        
        if [ "$POLICY_COUNT" -eq 0 ]; then
            echo "⚠️  No policies found, trying raw SQL methods..."
            # Try different methods to run raw SQL
            cat /app/scripts/raw_populate.sql | docker exec -i insureflow_db psql -U insureflow -d insureflow 2>/dev/null || \
            echo "⚠️  All raw SQL methods failed, will use absolute minimal fallback"
        else
            echo "ℹ️  Found $POLICY_COUNT policies, skipping raw SQL"
        fi
    }
    
    echo "⚠️  If raw SQL also fails, creating absolute minimal fallback..."
    python3 << 'END'
from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.broker import Broker
from app.models.company import InsuranceCompany
from app.models.policy import Policy, PolicyType, PolicyStatus
from app.models.premium import Premium, PaymentStatus, BillingCycle
from app.core.security import get_password_hash
from datetime import datetime, date, timedelta
from decimal import Decimal
import random

db = next(get_db())

# Check if users exist
user_count = db.query(User).count()
if user_count > 0:
    print(f"ℹ️  Database already has {user_count} user(s)")
    # Check if we have policies
    policy_count = db.query(Policy).count()
    if policy_count > 0:
        print(f"ℹ️  Database already has {policy_count} policies")
        db.close()
        exit(0)
    else:
        print("⚠️  No policies found, will create sample policies...")

print("✅ Creating minimal test data...")

# Create Insurance Company
company = db.query(InsuranceCompany).first()
if not company:
    company = InsuranceCompany(
        name='Secure Life Insurance Nigeria',
        registration_number='RC123456',
        address='14B Adeola Odeku Street, Victoria Island, Lagos',
        contact_email='info@securelife.ng',
        contact_phone='+234-1-234-5678',
        website='https://securelife.ng',
        description='Leading life insurance provider in Nigeria'
    )
    db.add(company)
    db.commit()
    print('✅ Created Insurance Company')

# Sarah Johnson (Insurance Admin)
sarah = db.query(User).filter_by(email='sarah.johnson@sovereigntrust.com').first()
if not sarah:
    sarah = User(
        email='sarah.johnson@sovereigntrust.com',
        username='sarah.johnson',
        full_name='Sarah Johnson',
        hashed_password=get_password_hash('password123'),
        role=UserRole.INSURANCE_ADMIN,
        is_active=True,
        is_verified=True
    )
    db.add(sarah)
    db.commit()
    print('✅ Created Sarah Johnson (Insurance Admin)')

# John Broker
john = db.query(User).filter_by(email='john.broker@scib.ng').first()
if not john:
    john = User(
        email='john.broker@scib.ng',
        username='john.broker',
        full_name='John Broker',
        hashed_password=get_password_hash('password123'),
        role=UserRole.BROKER,
        is_active=True,
        is_verified=True
    )
    db.add(john)
    db.flush()

    # Broker profile
    broker = Broker(
        user_id=john.id,
        name='SCIB',
        license_number='BRK-2023-001',
        agency_name='Sovereign Capital Investment Banking',
        contact_email='john.broker@scib.ng',
        contact_phone='+234-801-234-5678',
        office_address='Lagos, Nigeria',
        is_active=True
    )
    db.add(broker)
    db.commit()
    print('✅ Created John Broker')
else:
    broker = db.query(Broker).filter_by(user_id=john.id).first()

# Create Customer Users
customers = []
for i in range(5):
    email = f'customer{i+1}@example.com'
    customer = db.query(User).filter_by(email=email).first()
    if not customer:
        customer = User(
            email=email,
            username=f'customer{i+1}',
            full_name=f'Customer {i+1}',
            hashed_password=get_password_hash('password123'),
            role=UserRole.CUSTOMER,
            is_active=True,
            is_verified=True
        )
        db.add(customer)
        customers.append(customer)
db.commit()
if customers:
    print(f'✅ Created {len(customers)} customers')

# Get all customers
all_customers = db.query(User).filter_by(role=UserRole.CUSTOMER).all()

# Create Sample Policies with proper data
policies = []
policy_types = [PolicyType.LIFE, PolicyType.AUTO, PolicyType.HEALTH]
for i in range(8):
    policy_number = f'POL-{broker.license_number[-3:]}-2024-{i+1:04d}'
    
    existing_policy = db.query(Policy).filter_by(policy_number=policy_number).first()
    if existing_policy:
        policies.append(existing_policy)
        continue
    
    customer = random.choice(all_customers) if all_customers else john
    policy_type = random.choice(policy_types)
    
    # Generate realistic amounts
    premium_amounts = {
        PolicyType.LIFE: random.randint(200000, 800000),
        PolicyType.AUTO: random.randint(150000, 600000),
        PolicyType.HEALTH: random.randint(100000, 400000)
    }
    
    coverage_amounts = {
        PolicyType.LIFE: random.randint(5000000, 20000000),
        PolicyType.AUTO: random.randint(2000000, 10000000),
        PolicyType.HEALTH: random.randint(1000000, 5000000)
    }
    
    start_date = date.today() - timedelta(days=random.randint(30, 300))
    end_date = start_date + timedelta(days=365)
    
    try:
        policy = Policy(
            policy_number=policy_number,
            policy_name=f'{policy_type.value.title()} Insurance Policy',
            policy_type=policy_type,
            user_id=customer.id,
            company_id=company.id,
            broker_id=broker.id if broker else None,
            status=PolicyStatus.ACTIVE,
            start_date=start_date,
            end_date=end_date,
            due_date=end_date,
            premium_amount=Decimal(str(premium_amounts[policy_type])),
            coverage_amount=Decimal(str(coverage_amounts[policy_type])),
            company_name=f'Company {i+1}',
            contact_person=customer.full_name,
            contact_email=customer.email,
            contact_phone='+234-800-000-0000'
        )
        db.add(policy)
        policies.append(policy)
    except Exception as e:
        print(f"⚠️  Error creating policy {i+1}: {e}")
        # Create minimal policy without optional fields
        policy = Policy(
            policy_number=policy_number,
            policy_type=policy_type,
            user_id=customer.id,
            company_id=company.id,
            broker_id=broker.id if broker else None,
            status=PolicyStatus.ACTIVE,
            start_date=start_date,
            end_date=end_date,
            premium_amount=Decimal(str(premium_amounts[policy_type])),
            coverage_amount=Decimal(str(coverage_amounts[policy_type]))
        )
        db.add(policy)
        policies.append(policy)

db.commit()
print(f'✅ Created {len(policies)} policies')

# Create Sample Premiums
premiums_created = 0
for policy in policies:
    try:
        # Create 2-3 premiums per policy
        for j in range(random.randint(2, 3)):
            due_date = policy.start_date + timedelta(days=j*30)
            if due_date <= date.today():
                status = PaymentStatus.PAID if random.random() > 0.3 else PaymentStatus.PENDING
            else:
                status = PaymentStatus.PENDING
                
            premium = Premium(
                policy_id=policy.id,
                amount=float(policy.premium_amount),
                due_date=due_date,
                status=status.value if hasattr(status, 'value') else str(status),
                billing_cycle=BillingCycle.MONTHLY
            )
            db.add(premium)
            premiums_created += 1
    except Exception as e:
        print(f"⚠️  Error creating premium for policy {policy.id}: {e}")

db.commit()
print(f'✅ Created {premiums_created} premiums')

print(f'✅ Minimal test data created successfully!')
print(f'📊 Summary: {len(policies)} policies, {premiums_created} premiums')
db.close()
END
    }
}

echo "✅ Database setup complete!"
echo "🚀 Starting FastAPI application..."

# Start the FastAPI application
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} 