#!/bin/bash
# Fix Git conflicts on server by resetting to latest code

SERVER_HOST="${SERVER_HOST:-72.61.254.71}"
SERVER_USER="${SERVER_USER:-root}"
DEPLOY_DIR="${DEPLOY_DIR:-/opt/dice_game}"

echo "🔧 Fixing Git Conflicts on Server..."
echo "====================================="
echo ""

SSH_COMMANDS="
set -e
cd ${DEPLOY_DIR}

echo '📋 Current Git status:'
git status --short || true
echo ''

echo '💾 Stashing local changes...'
git stash || echo 'No changes to stash'
echo ''

echo '🔄 Resetting to latest code from repository...'
git fetch origin
git reset --hard origin/main
echo '✅ Code reset to latest version'
echo ''

echo '📊 Git status after reset:'
git status --short || true
echo ''

echo '✅ Git conflict resolved!'
"

echo "Running commands on server..."
ssh ${SERVER_USER}@${SERVER_HOST} "$SSH_COMMANDS"

echo ""
echo "✅ Server Git conflicts fixed!"
echo "Now you can deploy using:"
echo "  ssh ${SERVER_USER}@${SERVER_HOST} 'cd ${DEPLOY_DIR} && docker compose down && docker compose up -d --build'"
