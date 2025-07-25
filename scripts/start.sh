#!/bin/bash

# Run database migrations
alembic upgrade head

# Start the FastAPI application
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} 