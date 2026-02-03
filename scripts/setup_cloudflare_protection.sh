#!/bin/bash
# Setup Cloudflare protection to hide real server IP

set -e

if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (use sudo)"
    exit 1
fi

echo "🔐 Setting up Cloudflare Protection..."
echo "======================================"
echo ""
echo "STEP 1: Sign up for Cloudflare (if not done)"
echo "  - Go to: https://www.cloudflare.com"
echo "  - Sign up (Free plan works)"
echo ""
echo "STEP 2: Add your domain"
echo "  - Add domain: gunduata.online"
echo "  - Cloudflare will scan your DNS records"
echo ""
echo "STEP 3: Change Nameservers"
echo "  - Cloudflare will give you 2 nameservers"
echo "  - Update your domain registrar with these nameservers"
echo "  - Wait 24-48 hours for propagation"
echo ""
echo "STEP 4: Enable Proxy (CRITICAL)"
echo "  - In Cloudflare dashboard, find your DNS records"
echo "  - Click the 'Proxy' icon (should turn ORANGE)"
echo "  - This hides your real IP address"
echo ""
echo "STEP 5: Enable Security Settings"
echo "  - SSL/TLS: Full (strict)"
echo "  - Always Use HTTPS: ON"
echo "  - Under Attack Mode: ON (optional but recommended)"
echo ""
echo "STEP 6: Configure Server"
echo "  - Set ENFORCE_CLOUDFLARE_ONLY=True in .env"
echo "  - Run: ./scripts/block_direct_ip_access.sh"
echo ""
echo "RESULT:"
echo "  ✅ Your real IP (72.61.254.71) will be hidden"
echo "  ✅ All traffic goes through Cloudflare"
echo "  ✅ Hosting provider (AWS/GCP) can't trace requests to you"
echo "  ✅ Only Cloudflare IPs can access your server"
echo ""
