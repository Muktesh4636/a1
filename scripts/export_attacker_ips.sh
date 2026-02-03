#!/bin/bash
# Export all attacker IP addresses to a file

ATTACK_LOG="/opt/dice_game/backend/logs/attacks.log"
OUTPUT_FILE="/opt/dice_game/backend/logs/attacker_ips.txt"

echo "📋 Extracting attacker IP addresses..."

if [ -f "$ATTACK_LOG" ]; then
    # Extract unique IP addresses from attack log
    grep -oP 'IP: \K[0-9.]+' "$ATTACK_LOG" 2>/dev/null | sort -u > "$OUTPUT_FILE"
    
    echo "✅ Extracted $(wc -l < $OUTPUT_FILE) unique attacker IPs"
    echo "📁 Saved to: $OUTPUT_FILE"
    echo ""
    echo "First 20 IPs:"
    head -20 "$OUTPUT_FILE"
else
    echo "No attack log found"
fi
