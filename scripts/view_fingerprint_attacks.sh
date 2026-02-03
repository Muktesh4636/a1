#!/bin/bash
# View fingerprint-based attacks (VPN-resistant tracking)

FINGERPRINT_LOG="/opt/dice_game/backend/logs/fingerprint_attacks.log"
ATTACK_LOG="/opt/dice_game/backend/logs/attacks.log"

echo "🔍 Fingerprint-Based Attack Logs (VPN-Resistant)"
echo "================================================="
echo ""

if [ -f "$FINGERPRINT_LOG" ]; then
    echo "📋 FINGERPRINT ATTACKS (works even if attacker uses VPN):"
    echo "--------------------------------------------------------"
    cat "$FINGERPRINT_LOG" | tail -50
    echo ""
    echo "Total fingerprint attacks logged: $(wc -l < $FINGERPRINT_LOG)"
    echo ""
    echo "Top attacking fingerprints:"
    grep -oP 'Fingerprint: \K[a-f0-9]+' "$FINGERPRINT_LOG" 2>/dev/null | sort | uniq -c | sort -rn | head -10
else
    echo "No fingerprint attack log file found yet"
fi

echo ""
echo ""

if [ -f "$ATTACK_LOG" ]; then
    echo "📋 ATTACKS WITH FINGERPRINT DATA:"
    echo "---------------------------------"
    grep "Fingerprint:" "$ATTACK_LOG" | tail -30
    echo ""
    echo "Total attacks with fingerprints: $(grep -c "Fingerprint:" "$ATTACK_LOG" 2>/dev/null || echo 0)"
fi

echo ""
echo "💡 Fingerprint tracking works even if attackers use VPNs!"
echo "💡 To view live fingerprint attacks: tail -f $FINGERPRINT_LOG"
