#!/bin/bash

# Script to restart deployment server
# Run this AFTER SSHing into your deployment server

set -e

echo "🔄 Restarting Deployment Server..."
echo "=================================="
echo ""

# Navigate to deployment directory
DEPLOY_DIR="/opt/dice_game"
if [ ! -d "$DEPLOY_DIR" ]; then
    echo "⚠️  Deployment directory not found at $DEPLOY_DIR"
    echo "Please update DEPLOY_DIR variable or create the directory"
    exit 1
fi

cd "$DEPLOY_DIR"

echo "📂 Working directory: $(pwd)"
echo ""

# Pull latest code
echo "📥 Pulling latest code from repository..."
git fetch origin
git reset --hard origin/main
echo "✅ Code updated"
echo ""

# Stop all services
echo "🛑 Stopping all services..."
docker compose down
echo "✅ Services stopped"
echo ""

# Rebuild and start services
echo "🔨 Rebuilding and starting services..."
docker compose up -d --build
echo "✅ Services started"
echo ""

# Wait for services to initialize
echo "⏳ Waiting for services to initialize..."
sleep 10
echo ""

# Check service status
echo "📊 Service Status:"
echo "=================="
docker compose ps
echo ""

# Test server response
echo "🧪 Testing server response..."
sleep 5
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8232/ 2>/dev/null || echo "000")

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Server is responding (HTTP 200)"
else
    echo "⚠️  Server returned HTTP $HTTP_CODE"
    echo "Check logs with: docker compose logs web"
fi
echo ""

# Show recent logs
echo "📋 Recent Web Server Logs (last 10 lines):"
echo "=========================================="
docker compose logs --tail=10 web
echo ""

# Show timer service status
echo "⏱️  Timer Service Status:"
echo "========================"
if docker compose ps | grep -q "game_timer.*Up"; then
    echo "✅ Timer service is running"
    echo "Recent logs:"
    docker compose logs --tail=5 game_timer
else
    echo "⚠️  Timer service is not running!"
    echo "Start it with: docker compose up -d game_timer"
fi
echo ""

echo "✅ Deployment server restart complete!"
echo ""
echo "🔍 Useful commands:"
echo "  - View logs: docker compose logs -f web"
echo "  - Check status: docker compose ps"
echo "  - Test API: curl http://localhost:8232/api/"
echo ""












