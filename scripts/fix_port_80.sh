#!/bin/bash
# Fix port 80 conflict on server

SERVER_HOST="${SERVER_HOST:-72.61.254.71}"
SERVER_USER="${SERVER_USER:-root}"

echo "🔍 Checking what's using port 80..."
echo "===================================="
echo ""

SSH_COMMANDS="
echo '📋 Checking processes using port 80...'
echo '--------------------------------------'
lsof -i :80 || netstat -tulpn | grep :80 || ss -tulpn | grep :80 || echo 'No process found (may need root)'
echo ''

echo '🔍 Checking Docker containers using port 80...'
docker ps --format 'table {{.Names}}\t{{.Ports}}' | grep :80 || echo 'No Docker containers found'
echo ''

echo '🛑 Stopping services that might use port 80...'
systemctl stop nginx 2>/dev/null || echo 'Nginx not running or not installed'
systemctl stop apache2 2>/dev/null || echo 'Apache not running or not installed'
systemctl stop httpd 2>/dev/null || echo 'Httpd not running or not installed'
echo ''

echo '🔪 Killing processes on port 80...'
fuser -k 80/tcp 2>/dev/null || echo 'No process to kill'
sleep 2
echo ''

echo '✅ Port 80 should now be free'
echo ''
echo '📊 Current port 80 status:'
lsof -i :80 2>/dev/null || netstat -tulpn | grep :80 2>/dev/null || ss -tulpn | grep :80 2>/dev/null || echo 'Port 80 is free ✅'
"

ssh ${SERVER_USER}@${SERVER_HOST} "$SSH_COMMANDS"

echo ""
echo "Now you can restart Docker containers:"
echo "ssh ${SERVER_USER}@${SERVER_HOST} 'cd /opt/dice_game && docker compose up -d'"
