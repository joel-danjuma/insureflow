#!/bin/bash

# InsureFlow Notification System Deployment Script
# Run this on your VPS to deploy the notification-based reminder system

echo "🚀 Starting InsureFlow Notification System Deployment..."
echo "=================================================="

# Step 1: Pull latest code
echo "📥 Step 1: Pulling latest code from repository..."
git pull origin main

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to pull latest code. Please check git status."
    exit 1
fi

echo "✅ Code updated successfully!"

# Step 2: Stop current services
echo "🛑 Step 2: Stopping current services..."
docker compose -f docker-compose.prod.yml down

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to stop services."
    exit 1
fi

echo "✅ Services stopped successfully!"

# Step 3: Rebuild services (backend and frontend)
echo "🔨 Step 3: Rebuilding backend and frontend services..."
docker compose -f docker-compose.prod.yml build backend frontend

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to rebuild services."
    exit 1
fi

echo "✅ Services rebuilt successfully!"

# Step 4: Start services
echo "🚀 Step 4: Starting all services..."
docker compose -f docker-compose.prod.yml up -d

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to start services."
    exit 1
fi

echo "✅ Services started successfully!"

# Step 5: Wait for services to be ready
echo "⏳ Step 5: Waiting for services to be ready..."
sleep 30

# Check if backend is healthy
echo "🔍 Checking backend health..."
for i in {1..10}; do
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend is healthy!"
        break
    elif [ $i -eq 10 ]; then
        echo "❌ Error: Backend failed to start properly."
        exit 1
    else
        echo "⏳ Waiting for backend... (attempt $i/10)"
        sleep 10
    fi
done

# Step 6: Run database migration
echo "🗄️  Step 6: Running database migration for notifications table..."
docker compose -f docker-compose.prod.yml exec backend alembic upgrade head

if [ $? -ne 0 ]; then
    echo "❌ Error: Database migration failed."
    echo "💡 Trying alternative migration method..."
    
    # Alternative: Run migration directly in container
    docker compose -f docker-compose.prod.yml exec backend python -c "
from alembic.config import Config
from alembic import command
import os

# Set up Alembic config
alembic_cfg = Config('/app/alembic.ini')
alembic_cfg.set_main_option('script_location', '/app/alembic')

# Run upgrade
try:
    command.upgrade(alembic_cfg, 'head')
    print('✅ Migration completed successfully!')
except Exception as e:
    print(f'❌ Migration failed: {e}')
    exit(1)
"
    
    if [ $? -ne 0 ]; then
        echo "❌ Error: Both migration methods failed."
        echo "🔧 Manual migration required. See troubleshooting section below."
        exit 1
    fi
fi

echo "✅ Database migration completed successfully!"

# Step 7: Verify services are running
echo "🔍 Step 7: Verifying all services are running..."
docker compose -f docker-compose.prod.yml ps

# Step 8: Test the notification system
echo "🧪 Step 8: Testing notification system..."
curl -X POST http://localhost:8000/api/v1/reminders/test-notifications \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ Notification system test endpoint is accessible!"
else
    echo "⚠️  Warning: Could not test notification system (may need authentication)"
fi

# Step 9: Show final status
echo ""
echo "🎉 DEPLOYMENT COMPLETE!"
echo "======================="
echo "✅ Code updated"
echo "✅ Services rebuilt and started"
echo "✅ Database migration completed"
echo "✅ Notification system ready"
echo ""
echo "🌐 Your services are running at:"
echo "   Frontend: http://your-vps-ip:3000"
echo "   Backend:  http://your-vps-ip:8000"
echo ""
echo "🔔 The notification system is now active:"
echo "   - Admins can send automatic payment reminders"
echo "   - Brokers will receive notifications in their dashboards"
echo "   - 30-day overdue limit with 24h cooldown"
echo ""
echo "📊 To test the system:"
echo "   1. Log in as an admin to the Insurance Firm Dashboard"
echo "   2. Click 'Send Payment Reminders'"
echo "   3. Check the success message for notification details"
echo ""

# Show container status
echo "📋 Current container status:"
docker compose -f docker-compose.prod.yml ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "🚀 Deployment completed successfully!" 