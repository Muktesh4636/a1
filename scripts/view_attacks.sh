#!/bin/bash
# View all attack attempts and blocked IPs

ATTACK_LOG="/opt/dice_game/backend/logs/attacks.log"
BLOCKED_LOG="/opt/dice_game/backend/logs/blocked_ips.log"

echo "🔍 Attack Logs and Blocked IPs"
echo "==============================="
echo ""

if [ -f "$ATTACK_LOG" ]; then
    echo "📋 ATTACK ATTEMPTS (with IP addresses):"
    echo "--------------------------------------"
    cat "$ATTACK_LOG" | tail -50
    echo ""
    echo "Total attacks logged: $(wc -l < $ATTACK_LOG)"
else
    echo "No attack log file found yet"
fi

echo ""
echo ""

if [ -f "$BLOCKED_LOG" ]; then
    echo "🚫 PERMANENTLY BLOCKED IPs:"
    echo "---------------------------"
    cat "$BLOCKED_LOG" | tail -50
    echo ""
    echo "Total IPs blocked: $(wc -l < $BLOCKED_LOG)"
else
    echo "No blocked IPs log file found yet"
fi

echo ""
echo ""
echo "📊 ATTACK STATISTICS:"
echo "---------------------"
if [ -f "$ATTACK_LOG" ]; then
    echo "Top attacking IPs:"
    grep -oP 'IP: \K[0-9.]+' "$ATTACK_LOG" 2>/dev/null | sort | uniq -c | sort -rn | head -10
    echo ""
    echo "Attack types:"
    grep -oP 'Type: \K\w+' "$ATTACK_LOG" 2>/dev/null | sort | uniq -c | sort -rn
fi

echo ""
echo "💡 To view live attacks: tail -f $ATTACK_LOG"
