#!/bin/bash
# Aggressively block attacking IP addresses

if [ "$#" -lt 1 ]; then
    echo "Usage: $0 <IP_ADDRESS>"
    echo "Example: $0 192.168.1.100"
    exit 1
fi

IP=$1

echo "🔒 Permanently blocking attacker IP: $IP"

# Block with UFW
ufw deny from $IP 2>/dev/null || true

# Block with iptables
iptables -A INPUT -s $IP -j DROP 2>/dev/null || true
iptables -A OUTPUT -d $IP -j DROP 2>/dev/null || true

# Add to Fail2Ban
fail2ban-client set sshd banip $IP 2>/dev/null || true

# Block in Docker network
docker network inspect dice_game_dice_game_network 2>/dev/null | grep -q $IP || \
iptables -I DOCKER-USER -s $IP -j DROP 2>/dev/null || true

# Log the block
echo "$(date): Permanently blocked $IP" >> /opt/dice_game/backend/logs/blocked_ips.log

echo "✅ IP $IP has been permanently blocked on all layers"
