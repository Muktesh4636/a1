#!/bin/bash

# Deployment Server Monitoring Script
# This script monitors the deployment server for common issues

echo "🔍 Deployment Server Health Check"
echo "=================================="
echo ""

SERVER_HOST="${SERVER_HOST:-159.198.46.36}"
SERVER_USER="${SERVER_USER:-root}"
DEPLOY_DIR="${DEPLOY_DIR:-/opt/dice_game}"

ssh ${SERVER_USER}@${SERVER_HOST} << 'EOF'
cd /opt/dice_game

echo "📊 Container Status:"
docker compose ps
echo ""

echo "💾 Memory Usage:"
docker stats --no-stream --format 'table {{.Name}}\t{{.MemUsage}}\t{{.MemPerc}}' | grep dice_game
echo ""

echo "🔍 Recent Errors (last 100 lines):"
docker compose logs --tail=100 2>&1 | grep -iE '(error|exception|traceback|failed|crash|killed|oom|timeout|connection.*refused|database.*does.*not.*exist)' | tail -20
echo ""

echo "📋 Database Connection Test:"
docker compose exec -T db psql -U postgres -d dice_game -c 'SELECT 1;' 2>&1 | head -3
echo ""

echo "📋 Redis Connection Test:"
docker compose exec -T redis redis-cli -a "${REDIS_PASSWORD:-redis_password_change_me}" ping 2>&1
echo ""

echo "🔄 Container Restart History:"
docker ps -a --filter "name=dice_game" --format "{{.Names}}: {{.Status}}" | head -10
echo ""

echo "💿 Disk Space:"
df -h / | tail -1
echo ""

echo "✅ Health check complete!"
EOF












