#!/bin/bash
# Script to manually block/unblock IP addresses

if [ "$#" -lt 2 ]; then
    echo "Usage: $0 [block|unblock] <IP_ADDRESS>"
    echo "Example: $0 block 192.168.1.100"
    exit 1
fi

ACTION=$1
IP=$2

if [ "$ACTION" == "block" ]; then
    echo "Blocking IP: $IP"
    # Block with UFW
    ufw deny from $IP
    # Block with iptables
    iptables -A INPUT -s $IP -j DROP
    # Add to Fail2Ban
    fail2ban-client set sshd banip $IP
    echo "✓ IP $IP has been blocked"
elif [ "$ACTION" == "unblock" ]; then
    echo "Unblocking IP: $IP"
    # Unblock with UFW
    ufw delete deny from $IP
    # Unblock with iptables
    iptables -D INPUT -s $IP -j DROP
    # Remove from Fail2Ban
    fail2ban-client set sshd unbanip $IP
    echo "✓ IP $IP has been unblocked"
else
    echo "Invalid action. Use 'block' or 'unblock'"
    exit 1
fi
