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

# Create initial test users if database is empty
echo "👥 Checking for initial users..."
python3 << 'END'
from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.broker import Broker
from app.core.security import get_password_hash

db = next(get_db())

# Check if users exist
user_count = db.query(User).count()
if user_count > 0:
    print(f"ℹ️  Database already has {user_count} user(s), skipping user creation.")
    db.close()
    exit(0)

print("✅ Creating initial test users...")

# Create Sarah Johnson (Insurance Admin)
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

# Create John Broker
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

# Create broker profile for John
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
print('✅ Created John Broker with profile')

print(f'✅ Initial users created successfully!')
db.close()
END

echo "✅ Database setup complete!"
echo "🚀 Starting FastAPI application..."

# Start the FastAPI application
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} 