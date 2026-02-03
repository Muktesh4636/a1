#!/bin/bash
# View API-specific attack logs

API_ATTACK_LOG="/opt/dice_game/backend/logs/api_attacks.log"
ATTACK_LOG="/opt/dice_game/backend/logs/attacks.log"

echo "🔍 API Attack Logs"
echo "=================="
echo ""

if [ -f "$API_ATTACK_LOG" ]; then
    echo "📋 API-SPECIFIC ATTACKS:"
    echo "------------------------"
    cat "$API_ATTACK_LOG" | tail -50
    echo ""
    echo "Total API attacks logged: $(wc -l < $API_ATTACK_LOG)"
else
    echo "No API attack log file found yet"
fi

echo ""
echo ""

if [ -f "$ATTACK_LOG" ]; then
    echo "📋 ALL ATTACKS (including API):"
    echo "-------------------------------"
    grep -i "api" "$ATTACK_LOG" | tail -30
    echo ""
    echo "Total API attacks in main log: $(grep -i "api" "$ATTACK_LOG" | wc -l)"
fi

echo ""
echo "💡 To view live API attacks: tail -f $API_ATTACK_LOG"
