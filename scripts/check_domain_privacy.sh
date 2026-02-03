#!/bin/bash
# Check if domain WHOIS information is private

DOMAIN="gunduata.online"

echo "Checking WHOIS privacy for $DOMAIN..."
echo "======================================"
echo ""

# Check WHOIS information
whois_result=$(whois $DOMAIN 2>/dev/null || echo "Error querying WHOIS")

# Check for privacy indicators
if echo "$whois_result" | grep -qi "privacy\|proxy\|protected\|redacted\|whois privacy"; then
    echo "✅ Domain privacy appears to be ENABLED"
    echo ""
    echo "Privacy indicators found in WHOIS"
else
    echo "⚠️  Domain privacy may NOT be enabled"
    echo ""
    echo "WHOIS information may reveal:"
    echo "  - Registrant name"
    echo "  - Email address"
    echo "  - Physical address"
    echo "  - Phone number"
    echo ""
    echo "ACTION REQUIRED:"
    echo "  1. Enable WHOIS Privacy at your registrar"
    echo "  2. Or transfer domain to Cloudflare (free privacy)"
    echo ""
fi

echo "Full WHOIS output:"
echo "------------------"
echo "$whois_result" | head -30
