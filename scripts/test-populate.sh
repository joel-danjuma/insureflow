#!/bin/bash

# Test Database Population Script
# Run this locally to test the database population before VPS deployment

echo "🧪 Testing Database Population Locally..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if containers are running
if ! docker ps | grep insureflow > /dev/null; then
    echo "❌ InsureFlow containers are not running. Please start them first:"
    echo "   docker compose up -d"
    exit 1
fi

echo "✅ Docker containers are running"

# Run database migrations first
echo "🔄 Running database migrations..."
if docker exec insureflow_app alembic upgrade head; then
    echo "✅ Database migrations completed"
else
    echo "❌ Database migrations failed"
    exit 1
fi

# Test the population script
echo "🔄 Testing database population..."
if docker exec insureflow_app python scripts/populate_database.py; then
    echo "✅ Database population test successful!"
    echo ""
    echo "🎯 Test Login Credentials:"
    echo "   Admin: admin@securelife.ng / password123"
    echo "   Broker: ethan.carter@brokers.ng / password123"
    echo ""
    echo "🌐 Access your application at:"
    echo "   Frontend: http://localhost:3000"
    echo "   API Docs: http://localhost:8000/api/v1/docs"
else
    echo "❌ Database population test failed"
    exit 1
fi 