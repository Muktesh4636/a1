#!/bin/bash
# Complete deployment script - handles everything

SERVER_HOST="${SERVER_HOST:-72.61.254.71}"
SERVER_USER="${SERVER_USER:-root}"
DEPLOY_DIR="${DEPLOY_DIR:-/opt/dice_game}"

echo "🚀 Complete Deployment to Server"
echo "=================================="
echo ""

SSH_COMMANDS="
set -e
cd ${DEPLOY_DIR}

echo '📦 Step 1: Updating code from Git...'
git fetch origin
git stash || echo 'No changes to stash'
git reset --hard origin/main
echo '✅ Code updated'
echo ''

echo '🛑 Step 2: Stopping all containers...'
docker compose down || true
echo '✅ Containers stopped'
echo ''

echo '🔍 Step 2.5: Freeing port 80...'
fuser -k 80/tcp 2>/dev/null || true
systemctl stop nginx 2>/dev/null || true
systemctl stop apache2 2>/dev/null || true
systemctl stop httpd 2>/dev/null || true
sleep 2
echo '✅ Port 80 freed'
echo ''

echo '🧹 Step 3: Cleaning up old containers...'
docker rm -f dice_game_redis dice_game_db dice_game_web dice_game_game_timer 2>/dev/null || true
echo '✅ Old containers removed'
echo ''

echo '🔄 Step 4: Rebuilding and starting services...'
docker compose up -d --build --force-recreate
echo '✅ Services started'
echo ''

echo '⏳ Step 5: Waiting for services to initialize...'
sleep 15
echo ''

echo '📊 Step 6: Checking service status...'
docker compose ps
echo ''

echo '🔍 Step 7: Testing server response...'
sleep 5
HTTP_CODE=\$(curl -s -o /dev/null -w '%{http_code}' http://localhost:80/ 2>/dev/null || echo '000')
if [ \"\$HTTP_CODE\" = '200' ]; then
    echo '✅ Server is responding (HTTP 200)'
else
    echo '⚠️  Server returned HTTP \$HTTP_CODE'
    echo 'Checking logs...'
    docker compose logs --tail=50 web
fi

echo ''
echo '✅ Deployment complete!'
echo '🌐 Server URL: http://${SERVER_HOST}/'
echo '🔐 Admin Login: http://${SERVER_HOST}/game-admin/login/'
"

echo "Deploying to: ${SERVER_USER}@${SERVER_HOST}"
echo ""

ssh ${SERVER_USER}@${SERVER_HOST} "$SSH_COMMANDS"

echo ""
echo "✅ Deployment finished!"
