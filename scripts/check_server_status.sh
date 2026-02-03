#!/bin/bash
# Check server status and verify deployment

SERVER_HOST="${SERVER_HOST:-72.61.254.71}"
SERVER_USER="${SERVER_USER:-root}"
DEPLOY_DIR="${DEPLOY_DIR:-/opt/dice_game}"

echo "🔍 Checking Server Status..."
echo "============================="
echo ""

SSH_COMMANDS="
cd ${DEPLOY_DIR}

echo '📊 Container Status:'
echo '-------------------'
docker compose ps
echo ''

echo '🌐 Testing HTTP Response:'
echo '------------------------'
HTTP_CODE=\$(curl -s -o /dev/null -w '%{http_code}' http://localhost:80/ 2>/dev/null || echo '000')
if [ \"\$HTTP_CODE\" = '200' ]; then
    echo '✅ Server is responding (HTTP 200)'
elif [ \"\$HTTP_CODE\" = '000' ]; then
    echo '❌ Server not responding'
else
    echo \"⚠️  Server returned HTTP \$HTTP_CODE\"
fi
echo ''

echo '📋 Recent Web Logs (last 10 lines):'
echo '-----------------------------------'
docker compose logs --tail=10 web 2>/dev/null || echo 'No logs available'
echo ''

echo '🔗 Access URLs:'
echo '--------------'
echo \"🌐 Main Site: http://${SERVER_HOST}/\"
echo \"🔐 Admin Panel: http://${SERVER_HOST}/game-admin/login/\"
echo \"📊 API: http://${SERVER_HOST}/api/\"
"

ssh ${SERVER_USER}@${SERVER_HOST} "$SSH_COMMANDS"

echo ""
echo "✅ Status check complete!"
