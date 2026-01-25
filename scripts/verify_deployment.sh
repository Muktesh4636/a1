#!/bin/bash

# Script to verify deployment server is working correctly
# Run this on your deployment server

echo "🔍 Verifying Deployment Server..."
echo "=================================="
echo ""

cd /opt/dice_game || exit 1

# 1. Check all services status
echo "1. Service Status:"
echo "=================="
docker compose ps
echo ""

# 2. Check web service logs for errors
echo "2. Web Service Logs (last 20 lines):"
echo "===================================="
docker compose logs --tail=20 web | grep -i error || echo "✅ No errors found in recent logs"
echo ""

# 3. Test HTTP endpoint
echo "3. Testing HTTP Endpoint:"
echo "========================"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8232/ 2>/dev/null || echo "000")
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Server responding (HTTP $HTTP_CODE)"
else
    echo "❌ Server returned HTTP $HTTP_CODE"
fi
echo ""

# 4. Test API endpoint
echo "4. Testing API Endpoint:"
echo "======================="
API_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8232/api/ 2>/dev/null || echo "000")
if [ "$API_CODE" = "200" ] || [ "$API_CODE" = "401" ] || [ "$API_CODE" = "404" ]; then
    echo "✅ API responding (HTTP $API_CODE)"
else
    echo "⚠️  API returned HTTP $API_CODE"
fi
echo ""

# 5. Check timer service logs
echo "5. Timer Service Status:"
echo "======================="
if docker compose ps | grep -q "game_timer.*Up"; then
    echo "✅ Timer service is running"
    echo "Recent activity:"
    docker compose logs --tail=5 game_timer | grep -E "Timer:|Broadcast|✓" || echo "   (No recent timer logs)"
else
    echo "❌ Timer service is not running!"
fi
echo ""

# 6. Check database connection
echo "6. Database Connection:"
echo "======================"
if docker compose exec -T db psql -U postgres -d dice_game -c "SELECT 1;" > /dev/null 2>&1; then
    echo "✅ Database connection successful"
else
    echo "❌ Database connection failed"
fi
echo ""

# 7. Check Redis connection
echo "7. Redis Connection:"
echo "==================="
if docker compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis connection successful"
else
    echo "❌ Redis connection failed"
fi
echo ""

# Summary
echo "=================================="
echo "📋 Summary:"
echo "=================================="
ALL_UP=$(docker compose ps | grep -c "Up")
echo "Services running: $ALL_UP/4"
echo ""

if [ "$HTTP_CODE" = "200" ] && [ "$ALL_UP" = "4" ]; then
    echo "✅ All services are running and responding!"
    echo ""
    echo "🌐 Server URL: http://159.198.46.36:8232/"
    echo "🔌 WebSocket: ws://159.198.46.36:8232/ws/game/"
else
    echo "⚠️  Some services may need attention"
    echo ""
    echo "Check logs:"
    echo "  docker compose logs web"
    echo "  docker compose logs game_timer"
fi












