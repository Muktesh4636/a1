#!/bin/bash

# SAFE Restart Script - Preserves Database Data
# This script restarts services WITHOUT deleting volumes

echo "🔄 SAFE Restart - Preserving Database Data..."
echo "=============================================="
echo ""

# Server details
SERVER_HOST="${SERVER_HOST:-159.198.46.36}"
SERVER_USER="${SERVER_USER:-root}"
DEPLOY_DIR="${DEPLOY_DIR:-/opt/dice_game}"

echo "Server: ${SERVER_USER}@${SERVER_HOST}"
echo "Deployment directory: ${DEPLOY_DIR}"
echo ""
echo "⚠️  This script will preserve all database data"
echo ""

# SAFE commands - NO -v flag to preserve volumes
SSH_COMMANDS="
set -e
cd ${DEPLOY_DIR}

echo '📦 Pulling latest code...'
git fetch origin
git reset --hard origin/main

echo '🔄 Restarting Docker services (PRESERVING volumes)...'
# CRITICAL: Use 'docker compose down' WITHOUT -v flag to preserve database
docker compose down
docker compose up -d --build

echo '⏳ Waiting for services to start...'
sleep 10

echo '✅ Checking service status...'
docker compose ps

echo '🔍 Testing server response...'
sleep 5
HTTP_CODE=\$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8232/ || echo '000')
if [ \"\$HTTP_CODE\" = '200' ]; then
    echo '✅ Server is responding (HTTP 200)'
else
    echo '⚠️  Server returned HTTP \$HTTP_CODE'
fi

echo ''
echo '✅ SAFE restart complete - Database data preserved!'
"

# Check if running locally or need to SSH
if [ "$1" = "local" ] || [ -d "${DEPLOY_DIR}" ]; then
    echo "Running commands locally..."
    eval "$SSH_COMMANDS"
else
    echo "Connecting to remote server via SSH..."
    echo ""
    echo "Run these commands on your deployment server:"
    echo "----------------------------------------------"
    echo "$SSH_COMMANDS"
fi






