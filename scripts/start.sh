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
# Try upgrade head first, fallback to heads if multiple heads exist
set +e  # Temporarily disable exit on error
alembic upgrade head 2>&1 | tee /tmp/alembic_output.log
MIGRATION_EXIT_CODE=${PIPESTATUS[0]}
set -e  # Re-enable exit on error

if [ $MIGRATION_EXIT_CODE -ne 0 ]; then
    if grep -q "Multiple head revisions" /tmp/alembic_output.log; then
        echo "⚠️ Multiple heads detected, applying all heads..."
        alembic upgrade heads
    else
        echo "❌ Migration failed. Check logs above."
        exit 1
    fi
else
    echo "✅ Migrations applied successfully"
fi

# Populate database with comprehensive demo data
echo "👥 Populating database..."
python3 scripts/populate_database.py

# Create the InsureFlow admin user
echo "👑 Creating InsureFlow admin user..."
python3 scripts/fix_insureflow_admin.py

echo "✅ Database setup complete!"
echo "🚀 Starting FastAPI application..."

# Start the FastAPI application
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} 