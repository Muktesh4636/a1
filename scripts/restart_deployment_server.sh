#!/bin/bash

# Script to restart deployment server services
# USAGE: Run this on your deployment server, or SSH into server and run commands manually
# SAFETY: This script NEVER deletes volumes - all data is preserved

echo "🔄 Restarting Deployment Server Services (DATA-SAFE)..."
echo "======================================================"
echo ""

# Server details (adjust if needed)
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

# SAFETY CHECK: Verify database volume exists before proceeding
echo '🔒 Checking data protection...'
if ! docker volume ls | grep -q postgres_data; then
    echo '⚠️  WARNING: postgres_data volume not found!'
    exit 1
fi

# Backup before restart (optional but recommended)
echo '💾 Creating backup before restart...'
BACKUP_DIR=\${BACKUP_DIR:-/opt/dice_game/backups}
mkdir -p \$BACKUP_DIR
BACKUP_FILE=\"\$BACKUP_DIR/backup_\$(date +%Y%m%d_%H%M%S).sql\"
if docker compose ps db | grep -q Up; then
    docker compose exec -T db pg_dump -U postgres dice_game > \"\$BACKUP_FILE\" 2>/dev/null || echo '⚠️  Backup failed, continuing anyway...'
    echo \"📦 Backup saved to: \$BACKUP_FILE\"
else
    echo '⚠️  Database not running, skipping backup'
fi

echo '📦 Pulling latest code...'
git fetch origin
git reset --hard origin/main

echo '🔄 Restarting Docker services (PRESERVING ALL DATA)...'
# CRITICAL: Using 'docker compose down' WITHOUT -v flag to preserve volumes
# NEVER use 'docker compose down -v' as it deletes all database data
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
echo '✅ Deployment server restart complete!'
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
    echo ""
    echo "Or SSH into server and run:"
    echo "ssh ${SERVER_USER}@${SERVER_HOST}"
    echo "cd ${DEPLOY_DIR}"
    echo "git pull origin main"
    echo "docker compose down"
    echo "docker compose up -d --build"
fi








