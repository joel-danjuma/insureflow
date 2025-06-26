#!/bin/bash

# Test Reminders API Script
# This script tests the reminder endpoints directly to debug issues

echo "🧪 Testing InsureFlow Reminders API..."
echo "======================================"

# Test 1: Check if backend is responsive
echo "🔍 Test 1: Checking backend health..."
curl -s http://localhost:8000/health | jq '.' || echo "❌ Backend not responding or jq not installed"

# Test 2: Check if reminders endpoint exists (without auth)
echo -e "\n🔍 Test 2: Testing reminders endpoint (expect 401 Unauthorized)..."
curl -s -X POST http://localhost:8000/api/v1/reminders/send-auto \
  -H "Content-Type: application/json" \
  -d '{"max_days_overdue": 30}' || echo "❌ Endpoint not found"

# Test 3: Check database tables
echo -e "\n🔍 Test 3: Checking database tables..."
docker compose -f docker-compose.prod.yml exec db psql -U $POSTGRES_USER -d $POSTGRES_DB -c "
SELECT 
  'notifications' as table_name, 
  CASE WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'notifications') 
    THEN 'EXISTS' ELSE 'MISSING' END as status
UNION ALL
SELECT 
  'policies' as table_name,
  CASE WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'policies') 
    THEN 'EXISTS' ELSE 'MISSING' END as status
UNION ALL  
SELECT 
  'users' as table_name,
  CASE WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'users') 
    THEN 'EXISTS' ELSE 'MISSING' END as status;
"

# Test 4: Check if we have any policies with brokers
echo -e "\n🔍 Test 4: Checking for policies with brokers..."
docker compose -f docker-compose.prod.yml exec db psql -U $POSTGRES_USER -d $POSTGRES_DB -c "
SELECT 
  COUNT(*) as total_policies,
  COUNT(CASE WHEN broker_id IS NOT NULL THEN 1 END) as policies_with_brokers
FROM policies;
"

# Test 5: Check Alembic migration status
echo -e "\n🔍 Test 5: Checking Alembic migration status..."
docker compose -f docker-compose.prod.yml exec backend alembic current || echo "❌ Alembic not working"

# Test 6: Show recent backend logs
echo -e "\n🔍 Test 6: Recent backend logs (last 20 lines)..."
docker compose -f docker-compose.prod.yml logs backend --tail=20 | grep -v "GET /health"

echo -e "\n✅ API Testing Complete!"
echo "📋 Summary:"
echo "   - If notifications table is MISSING, run the migration"
echo "   - If policies_with_brokers is 0, you need test data"
echo "   - Check backend logs for specific error messages"
echo "   - 401 Unauthorized is expected (need admin token)" 