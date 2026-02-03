#!/bin/bash

# Script to deploy code to server
# This will pull latest code and restart services on the deployment server

echo "🚀 Deploying Code to Server..."
echo "================================"
echo ""

SERVER_HOST="${SERVER_HOST:-72.61.254.71}"
SERVER_USER="${SERVER_USER:-root}"
DEPLOY_DIR="${DEPLOY_DIR:-/opt/dice_game}"

echo "Server: ${SERVER_USER}@${SERVER_HOST}"
echo "Deployment directory: ${DEPLOY_DIR}"
echo ""

# Commands to run on server
SSH_COMMANDS="
set -e
cd ${DEPLOY_DIR}

echo '📦 Pulling latest code from repository...'
git fetch origin
git reset --hard origin/main
echo '✅ Code updated'
echo ''

echo '🔄 Restarting Docker services...'
docker compose down
docker compose up -d --build
echo '✅ Services restarted'
echo ''

echo '⏳ Waiting for services to start...'
sleep 10

echo '📊 Service Status:'
docker compose ps
echo ''

echo '🔍 Testing server response...'
sleep 5
HTTP_CODE=\$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8232/ 2>/dev/null || echo '000')
if [ \"\$HTTP_CODE\" = '200' ]; then
    echo '✅ Server is responding (HTTP 200)'
else
    echo '⚠️  Server returned HTTP \$HTTP_CODE'
fi

echo ''
echo '✅ Deployment complete!'
echo '🌐 Server URL: http://${SERVER_HOST}:8232/'
echo '🔐 Admin Login: http://${SERVER_HOST}:8232/game-admin/login/'
"

# Check if running locally or need to SSH
if [ "$1" = "local" ] || [ -d "${DEPLOY_DIR}" ]; then
    echo "Running commands locally..."
    eval "$SSH_COMMANDS"
else
    echo "To deploy to server, SSH in and run:"
    echo "------------------------------------"
    echo "ssh ${SERVER_USER}@${SERVER_HOST}"
    echo ""
    echo "Then run these commands:"
    echo "------------------------"
    echo "$SSH_COMMANDS"
    echo ""
    echo "Or use this one-liner:"
    echo "----------------------"
    echo "ssh ${SERVER_USER}@${SERVER_HOST} 'cd ${DEPLOY_DIR} && git pull origin main && docker compose down && docker compose up -d --build'"
fi

