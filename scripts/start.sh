#!/bin/bash
set -e

echo "🚀 Starting InsureFlow Backend..."

# Optional: Basic database connectivity check (without migrations)
echo "⏳ Checking database connectivity..."
python3 << 'END'
import time
import sys
from sqlalchemy import create_engine, text
from app.core.config import settings

try:
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print("✅ Database is reachable!")
except Exception as e:
    print(f"⚠️ Database not reachable: {e}")
    print("🔄 Starting app anyway - migrations can be run separately")
END

echo "✅ Skipping migrations and population (run separately if needed)"
echo "🚀 Starting FastAPI application..."

# Start the FastAPI application directly
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}