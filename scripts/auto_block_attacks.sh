#!/bin/bash
# Monitor logs and automatically block attacking IPs

LOG_FILE="/opt/dice_game/backend/logs/attacks.log"
BLOCKED_FILE="/opt/dice_game/backend/logs/blocked_ips.log"

# Monitor attack log and auto-block
tail -f $LOG_FILE 2>/dev/null | while read line; do
    if echo "$line" | grep -q "IP:"; then
        IP=$(echo "$line" | grep -oP 'IP: \K[0-9.]+')
        if [ ! -z "$IP" ]; then
            echo "🚨 Attack detected from $IP - Auto-blocking..."
            /opt/dice_game/scripts/block_attacker.sh $IP
        fi
    fi
done
