#!/bin/bash

# Script to prevent accidental user deletion
# This script should be run before any database operations

DEPLOY_DIR="${DEPLOY_DIR:-/opt/dice_game}"
cd "$DEPLOY_DIR" || exit 1

echo "🔒 User Deletion Protection Check"
echo "=================================="
echo ""

# Check current user count
USER_COUNT=$(docker compose exec -T db psql -U postgres -d dice_game -t -c "SELECT COUNT(*) FROM accounts_user;" 2>/dev/null | tr -d ' ' || echo "0")

echo "Current users in database: $USER_COUNT"
echo ""

if [ "$USER_COUNT" = "0" ]; then
    echo "⚠️  WARNING: No users found in database!"
    echo ""
    echo "This could indicate:"
    echo "  1. Database was reset/flushed"
    echo "  2. Users were accidentally deleted"
    echo "  3. Migration issue"
    echo ""
    echo "Recommended actions:"
    echo "  1. Check backups: ls -lh /opt/dice_game/backups/"
    echo "  2. Check logs: docker compose logs web | grep -i user"
    echo "  3. Restore from backup if available"
    echo ""
    exit 1
fi

echo "✅ Users exist in database - protection check passed"
exit 0



