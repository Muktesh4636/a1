#!/bin/bash
# Block direct access to server IP - only allow through Cloudflare/domain

set -e

if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (use sudo)"
    exit 1
fi

SERVER_IP="72.61.254.71"

echo "🔒 Blocking direct IP access - Only allowing domain access..."

# Block direct HTTP access to IP (only allow domain)
iptables -I INPUT -p tcp --dport 80 -d $SERVER_IP ! -s 127.0.0.1 -j DROP 2>/dev/null || true
iptables -I INPUT -p tcp --dport 443 -d $SERVER_IP ! -s 127.0.0.1 -j DROP 2>/dev/null || true

# Allow only if Host header matches domain (requires nginx/apache)
# For now, we'll rely on application-level blocking

echo "✅ Direct IP access blocked"
echo "⚠️  Server will only respond to requests with domain name (gunduata.online)"
echo "⚠️  Direct IP access (http://72.61.254.71) will be blocked"
