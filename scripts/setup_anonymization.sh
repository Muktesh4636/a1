#!/bin/bash
# Setup script for maximum anonymity and anti-tracing

set -e

echo "🔒 Setting up anonymization and anti-tracing protection..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (use sudo)"
    exit 1
fi

# Disable system logging that could reveal information
echo "Disabling unnecessary system logs..."
systemctl stop rsyslog 2>/dev/null || true
systemctl disable rsyslog 2>/dev/null || true

# Configure log rotation to delete old logs quickly
cat > /etc/logrotate.d/dice-game-anon << 'EOF'
/opt/dice_game/backend/logs/*.log {
    daily
    rotate 1
    compress
    delaycompress
    missingok
    notifempty
    create 0600 root root
    postrotate
        # Clear logs after rotation
        find /opt/dice_game/backend/logs -name "*.log.*" -mtime +1 -delete
    endscript
}

/var/log/nginx/*.log {
    daily
    rotate 1
    compress
    delaycompress
    missingok
    notifempty
    create 0600 root root
    postrotate
        systemctl reload nginx
    endscript
}
EOF

# Clear existing logs
echo "Clearing existing logs..."
find /var/log -name "*.log" -type f -exec truncate -s 0 {} \; 2>/dev/null || true
find /opt/dice_game/backend/logs -name "*.log" -type f -exec truncate -s 0 {} \; 2>/dev/null || true

# Disable command history
echo "Disabling command history..."
export HISTSIZE=0
export HISTFILESIZE=0
unset HISTFILE
echo "export HISTSIZE=0" >> /root/.bashrc
echo "export HISTFILESIZE=0" >> /root/.bashrc
echo "unset HISTFILE" >> /root/.bashrc

# Configure kernel to not log connections
sysctl -w net.netfilter.nf_log.0=none 2>/dev/null || true

# Disable systemd journal logging (minimal)
mkdir -p /etc/systemd/journald.conf.d/
cat > /etc/systemd/journald.conf.d/00-minimal.conf << 'EOF'
[Journal]
Storage=volatile
SystemMaxUse=10M
SystemKeepFree=100M
MaxRetentionSec=1h
EOF

systemctl restart systemd-journald

# Configure Docker to not log sensitive information
mkdir -p /etc/docker/
cat >> /etc/docker/daemon.json << 'EOF'
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "1"
  }
}
EOF

echo "✅ Anonymization setup complete"
