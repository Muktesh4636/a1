#!/bin/bash
# Clear all logs to prevent tracing

echo "Clearing all logs..."

# Clear application logs
find /opt/dice_game/backend/logs -name "*.log" -type f -exec truncate -s 0 {} \; 2>/dev/null || true
find /opt/dice_game/backend/logs -name "*.log.*" -type f -delete 2>/dev/null || true

# Clear system logs
journalctl --vacuum-time=1s 2>/dev/null || true
find /var/log -name "*.log" -type f -exec truncate -s 0 {} \; 2>/dev/null || true
find /var/log -name "*.log.*" -type f -delete 2>/dev/null || true

# Clear Docker logs
docker compose logs --tail=0 2>/dev/null || true
find /var/lib/docker/containers -name "*.log" -exec truncate -s 0 {} \; 2>/dev/null || true

# Clear command history
history -c
export HISTSIZE=0
export HISTFILESIZE=0

echo "Logs cleared"
