#!/bin/bash
set -e

echo "🚀 Starting InsureFlow Backend..."

# Wait for database to be ready
echo "⏳ Waiting for database..."
python3 << END
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
alembic upgrade head || {
    echo "⚠️  Migrations failed, initializing database from scratch..."
    python3 scripts/init_db.py
}

# Create initial users if they don't exist
echo "👥 Ensuring initial users exist..."
python3 << END
from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.broker import Broker
from app.core.security import get_password_hash

try:
    db = next(get_db())
    
    # Sarah Johnson
    if not db.query(User).filter(User.email == 'sarah.johnson@sovereigntrust.com').first():
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
        print("✅ Created Sarah Johnson")
    
    # John Broker
    john = db.query(User).filter(User.email == 'john.broker@scib.ng').first()
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
        
        broker = Broker(
            user_id=john.id,
            name='SCIB',
            license_number='BRK-2023-001',
            agency_name='Sovereign Capital Investment Banking',
            contact_email='john.broker@scib.ng',
            is_active=True
        )
        db.add(broker)
        print("✅ Created John Broker")
    
    db.commit()
    print("✅ Initial users ready")
    db.close()
except Exception as e:
    print(f"ℹ️  User initialization: {e}")
END

echo "✅ Database setup complete!"
echo "🚀 Starting FastAPI application..."

# Start the FastAPI application
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} 