#!/bin/bash

# Script to fix deployment server restart issues
# Run this on your deployment server

set -e

echo "🔧 Fixing Deployment Server Issues..."
echo "======================================"
echo ""

cd /opt/dice_game || exit 1

# Step 1: Fix git issue
echo "1. Fixing git repository..."
git reset --hard origin/main
echo "✅ Git repository fixed"
echo ""

# Step 2: Check web service logs
echo "2. Checking web service logs for errors..."
echo "=========================================="
docker compose logs web | tail -30
echo ""

# Step 3: Check if web service is running
echo "3. Checking service status..."
docker compose ps
echo ""

# Step 4: Try to run migrations if needed
echo "4. Running database migrations..."
docker compose exec -T web python manage.py migrate --noinput || echo "⚠️  Migrations failed or service not accessible"
echo ""

# Step 5: Collect static files
echo "5. Collecting static files..."
docker compose exec -T web python manage.py collectstatic --noinput || echo "⚠️  Static files collection failed or service not accessible"
echo ""

# Step 6: Restart web service
echo "6. Restarting web service..."
docker compose restart web
sleep 5
echo ""

# Step 7: Check status again
echo "7. Final status check..."
docker compose ps
echo ""

# Step 8: Show recent logs
echo "8. Recent web service logs:"
echo "=========================="
docker compose logs --tail=20 web
echo ""

echo "✅ Fix script completed!"
echo ""
echo "If web service is still restarting, check logs:"
echo "  docker compose logs web | tail -50"












