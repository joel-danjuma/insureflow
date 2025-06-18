#!/bin/bash

# InsureFlow VPS Deployment Script
# This script automates the deployment process on your Hostinger VPS

set -e  # Exit on any error

echo "🚀 Starting InsureFlow VPS Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    print_error "docker-compose is not installed. Please install it and try again."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    print_warning ".env file not found. Please create one based on env.production template."
    echo "You can copy the template: cp env.production .env"
    echo "Then edit .env with your actual values."
    exit 1
fi

print_status "Environment file found ✓"

# Stop any existing containers
print_status "Stopping existing containers..."
docker compose -f docker-compose.prod.yml down || true

# Remove old images (optional - uncomment if you want to force rebuild)
# print_status "Removing old images..."
# docker compose -f docker-compose.prod.yml down --rmi all || true

# Build and start services
print_status "Building and starting services..."
docker compose -f docker-compose.prod.yml up -d --build

# Wait for services to be ready
print_status "Waiting for services to start..."
sleep 30

# Check if services are running
print_status "Checking service health..."

# Check FastAPI
if curl -f http://localhost:8000/api/v1/docs > /dev/null 2>&1; then
    print_status "FastAPI backend is running ✓"
else
    print_warning "FastAPI backend health check failed"
fi

# Check Next.js Frontend
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    print_status "Next.js frontend is running ✓"
else
    print_warning "Next.js frontend health check failed"
fi

# Check PostgreSQL
if docker exec insureflow_db pg_isready -U insureflow > /dev/null 2>&1; then
    print_status "PostgreSQL database is running ✓"
else
    print_warning "PostgreSQL database health check failed"
fi

# Check Redis
if docker exec -it insureflow_redis redis-cli ping | grep PONG > /dev/null 2>&1; then
    print_status "Redis is running ✓"
else
    print_warning "Redis health check failed"
fi

print_status "Deployment completed!"
echo ""
echo "📋 Service URLs (behind Nginx):"
echo "   Application: http://your_domain.com"
echo "   API Docs: http://your_domain.com/api/v1/docs"
echo ""
echo "🔧 Next steps:"
echo "   1. Configure Nginx using the nginx-vps.conf file"
echo "   2. Update your domain name in the Nginx config"
echo "   3. Set up SSL with Let's Encrypt (optional)"
echo ""
echo "📊 To view logs: docker compose -f docker-compose.prod.yml logs -f"
echo "🛑 To stop services: docker compose -f docker-compose.prod.yml down" 