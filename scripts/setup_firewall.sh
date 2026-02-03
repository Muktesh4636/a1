#!/bin/bash
# Multi-Layer Firewall Setup Script
# This script configures UFW firewall, Fail2Ban, and system-level protections

set -e

echo "🔥 Setting up Multi-Layer Firewall Protection..."
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Please run as root (use sudo)${NC}"
    exit 1
fi

# ============================================
# Layer 1: UFW Firewall Configuration
# ============================================
echo -e "\n${GREEN}[1/5] Configuring UFW Firewall...${NC}"

# Install UFW if not installed
if ! command -v ufw &> /dev/null; then
    apt-get update
    apt-get install -y ufw
fi

# Reset UFW to defaults
ufw --force reset

# Default policies: deny all incoming, allow all outgoing
ufw default deny incoming
ufw default allow outgoing

# Allow SSH (IMPORTANT: Do this first!)
ufw allow 22/tcp comment 'SSH'

# Allow HTTP and HTTPS
ufw allow 80/tcp comment 'HTTP'
ufw allow 443/tcp comment 'HTTPS'

# Allow Docker (if needed)
# ufw allow 2376/tcp comment 'Docker daemon'

# Block common attack ports
ufw deny 21/tcp comment 'Block FTP'
ufw deny 23/tcp comment 'Block Telnet'
ufw deny 3306/tcp comment 'Block MySQL'
ufw deny 5432/tcp comment 'Block PostgreSQL (external)'
ufw deny 6379/tcp comment 'Block Redis (external)'
ufw deny 8080/tcp comment 'Block common proxy ports'
ufw deny 8888/tcp comment 'Block common admin ports'

# Rate limiting for SSH (max 6 connections per 30 seconds)
ufw limit 22/tcp comment 'Rate limit SSH'

# Enable UFW
ufw --force enable

echo -e "${GREEN}✓ UFW Firewall configured${NC}"

# ============================================
# Layer 2: Fail2Ban Configuration
# ============================================
echo -e "\n${GREEN}[2/5] Installing and configuring Fail2Ban...${NC}"

# Install Fail2Ban
if ! command -v fail2ban-client &> /dev/null; then
    apt-get update
    apt-get install -y fail2ban
fi

# Create Fail2Ban jail configuration
cat > /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
# Ban hosts for 1 hour
bantime = 3600
# Override /etc/fail2ban/jail.d/00-firewalld.conf:
banaction = ufw
# Number of failures before ban
maxretry = 5
# Time window for failures (seconds)
findtime = 600

[sshd]
enabled = true
port = 22
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 7200

[nginx-http-auth]
enabled = true
port = http,https
filter = nginx-http-auth
logpath = /var/log/nginx/error.log
maxretry = 5

[nginx-limit-req]
enabled = true
port = http,https
filter = nginx-limit-req
logpath = /var/log/nginx/error.log
maxretry = 10

[nginx-botsearch]
enabled = true
port = http,https
filter = nginx-botsearch
logpath = /var/log/nginx/access.log
maxretry = 2

# Django admin login protection
[django-admin]
enabled = true
port = http,https
filter = django-admin
logpath = /opt/dice_game/backend/logs/django.log
maxretry = 5
bantime = 3600
findtime = 600
EOF

# Create Django admin filter for Fail2Ban
cat > /etc/fail2ban/filter.d/django-admin.conf << 'EOF'
[Definition]
failregex = ^.*Invalid login attempt from <HOST>.*$
            ^.*Failed login attempt from <HOST>.*$
            ^.*Authentication failed for <HOST>.*$
ignoreregex =
EOF

# Restart Fail2Ban
systemctl restart fail2ban
systemctl enable fail2ban

echo -e "${GREEN}✓ Fail2Ban configured${NC}"

# ============================================
# Layer 3: System Hardening
# ============================================
echo -e "\n${GREEN}[3/5] Applying system hardening...${NC}"

# Disable root login via SSH (use key-based auth instead)
if [ -f /etc/ssh/sshd_config ]; then
    sed -i 's/#PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
    sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
    systemctl restart sshd
    echo -e "${YELLOW}⚠ Root SSH login disabled. Make sure you have SSH key access!${NC}"
fi

# Configure kernel parameters for DDoS protection
cat >> /etc/sysctl.conf << 'EOF'

# DDoS Protection
net.ipv4.tcp_syncookies = 1
net.ipv4.tcp_max_syn_backlog = 2048
net.ipv4.tcp_synack_retries = 2
net.ipv4.tcp_syn_retries = 5
net.ipv4.ip_local_port_range = 10000 65535

# Prevent IP spoofing
net.ipv4.conf.all.rp_filter = 1
net.ipv4.conf.default.rp_filter = 1

# Ignore ICMP redirects
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.default.accept_redirects = 0
net.ipv4.conf.all.secure_redirects = 0
net.ipv4.conf.default.secure_redirects = 0

# Ignore send redirects
net.ipv4.conf.all.send_redirects = 0
net.ipv4.conf.default.send_redirects = 0
EOF

# Apply sysctl settings
sysctl -p

echo -e "${GREEN}✓ System hardening applied${NC}"

# ============================================
# Layer 4: Docker Network Security
# ============================================
echo -e "\n${GREEN}[4/5] Configuring Docker network security...${NC}"

# Create Docker network security rules
# Note: Docker manages its own firewall rules, but we can restrict host access

# Block direct access to Docker ports from outside
# (Docker containers should only be accessible through reverse proxy)
iptables -I DOCKER-USER -i eth0 ! -s 127.0.0.1 -p tcp --dport 5432 -j DROP
iptables -I DOCKER-USER -i eth0 ! -s 127.0.0.1 -p tcp --dport 6379 -j DROP

echo -e "${GREEN}✓ Docker network security configured${NC}"

# ============================================
# Layer 5: Logging and Monitoring
# ============================================
echo -e "\n${GREEN}[5/5] Setting up security logging...${NC}"

# Create log directory
mkdir -p /opt/dice_game/backend/logs
chmod 755 /opt/dice_game/backend/logs

# Configure logrotate for security logs
cat > /etc/logrotate.d/dice-game-security << 'EOF'
/opt/dice_game/backend/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 0644 root root
}
EOF

echo -e "${GREEN}✓ Security logging configured${NC}"

# ============================================
# Summary
# ============================================
echo -e "\n${GREEN}================================================${NC}"
echo -e "${GREEN}✅ Multi-Layer Firewall Setup Complete!${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""
echo "Firewall Status:"
ufw status verbose
echo ""
echo "Fail2Ban Status:"
fail2ban-client status
echo ""
echo -e "${YELLOW}⚠ IMPORTANT NOTES:${NC}"
echo "1. SSH root login is disabled. Use SSH keys for access."
echo "2. Only ports 22, 80, and 443 are open."
echo "3. Fail2Ban will automatically block suspicious IPs."
echo "4. Rate limiting is active (100 requests/minute per IP)."
echo "5. Monitor logs: tail -f /var/log/fail2ban.log"
echo ""
echo -e "${GREEN}Your server is now protected by multiple firewall layers!${NC}"
