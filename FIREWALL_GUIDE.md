# 🔥 Multi-Layer Firewall Protection Guide

This guide explains the comprehensive firewall protection system implemented to protect your server and accounts.

## 🛡️ Firewall Layers Implemented

### **Layer 1: Application-Level Firewall (Django Middleware)**
- ✅ IP Blacklist/Whitelist
- ✅ Rate limiting per IP (100 requests/minute)
- ✅ Brute force detection (10 failed attempts = 2 hour ban)
- ✅ Suspicious activity detection (SQL injection, XSS, path traversal)
- ✅ Automatic IP blocking for attacks

### **Layer 2: System Firewall (UFW)**
- ✅ Only ports 22 (SSH), 80 (HTTP), 443 (HTTPS) open
- ✅ All other ports blocked
- ✅ Rate limiting on SSH (6 connections/30 seconds)
- ✅ Blocks common attack ports (FTP, Telnet, MySQL, etc.)

### **Layer 3: Fail2Ban (Automatic IP Blocking)**
- ✅ Monitors SSH login attempts
- ✅ Monitors web server logs
- ✅ Automatically bans IPs after 5 failed attempts
- ✅ Ban duration: 1-2 hours
- ✅ Protects Django admin panel

### **Layer 4: System Hardening**
- ✅ DDoS protection (SYN flood protection)
- ✅ IP spoofing prevention
- ✅ Root SSH login disabled (key-based auth only)
- ✅ Kernel-level security parameters

### **Layer 5: Docker Network Security**
- ✅ Database port (5432) only accessible from localhost
- ✅ Redis port (6379) only accessible from localhost
- ✅ Containers isolated from external access

## 🚀 Quick Setup

### Step 1: Run Firewall Setup Script

```bash
ssh root@72.61.254.71
cd /opt/dice_game
chmod +x scripts/setup_firewall.sh
sudo ./scripts/setup_firewall.sh
```

This will:
- Configure UFW firewall
- Install and configure Fail2Ban
- Apply system hardening
- Set up security logging

### Step 2: Configure Environment Variables

Add to your `.env` file on the server:

```env
# IP Blocking
BLOCKED_IPS=192.168.1.100,10.0.0.50  # Comma-separated list of IPs to block
ADMIN_WHITELIST_IPS=your.office.ip,your.home.ip  # IPs allowed to access admin panel (leave empty to allow all)

# Rate Limiting
RATE_LIMIT_REQUESTS=100  # Max requests per IP per window
RATE_LIMIT_WINDOW=60     # Time window in seconds
```

### Step 3: Deploy Updated Code

```bash
ssh root@72.61.254.71 "cd /opt/dice_game && git pull origin main && docker compose up -d --build"
```

## 📋 Firewall Features

### **1. IP Blacklisting**
Block specific IP addresses permanently:

**Via Environment Variable:**
```env
BLOCKED_IPS=192.168.1.100,10.0.0.50
```

**Via Script:**
```bash
./scripts/block_ip.sh block 192.168.1.100
```

**Via Django Admin:**
- IPs are automatically blocked after attacks
- Check blocked IPs in Redis cache

### **2. Admin Panel IP Whitelisting**
Restrict admin panel access to specific IPs:

```env
ADMIN_WHITELIST_IPS=your.office.ip,your.home.ip
```

**Important**: If you set this, only these IPs can access `/game-admin/`. Leave empty to allow all.

### **3. Rate Limiting**
- **Default**: 100 requests per minute per IP
- **Exceeded**: IP blocked for 1 hour
- **Configurable**: Via `RATE_LIMIT_REQUESTS` and `RATE_LIMIT_WINDOW`

### **4. Brute Force Protection**
- **Failed Login Attempts**: Tracked per IP
- **Threshold**: 10 failed attempts
- **Action**: IP blocked for 2 hours
- **Reset**: Automatically after ban period

### **5. Suspicious Activity Detection**
Automatically blocks IPs attempting:
- SQL injection (`SELECT`, `UNION`, etc.)
- XSS attacks (`<script>`, etc.)
- Path traversal (`../`)
- Config file access (`.env`, `config.php`, etc.)
- WordPress/phpMyAdmin access attempts

## 🔍 Monitoring and Management

### Check Firewall Status

```bash
# UFW Status
ufw status verbose

# Fail2Ban Status
fail2ban-client status
fail2ban-client status sshd
fail2ban-client status django-admin

# View Blocked IPs
fail2ban-client get sshd banned
```

### View Security Logs

```bash
# Fail2Ban Logs
tail -f /var/log/fail2ban.log

# Application Logs
tail -f /opt/dice_game/backend/logs/django.log

# UFW Logs
tail -f /var/log/ufw.log
```

### Manually Block/Unblock IPs

```bash
# Block an IP
./scripts/block_ip.sh block 192.168.1.100

# Unblock an IP
./scripts/block_ip.sh unblock 192.168.1.100

# Or use UFW directly
ufw deny from 192.168.1.100
ufw delete deny from 192.168.1.100
```

## 🛠️ Advanced Configuration

### Customize Rate Limits

Edit `.env`:
```env
RATE_LIMIT_REQUESTS=200  # Increase for high-traffic sites
RATE_LIMIT_WINDOW=60     # Time window
```

### Adjust Fail2Ban Settings

Edit `/etc/fail2ban/jail.local`:
```ini
[django-admin]
maxretry = 5      # Failed attempts before ban
bantime = 3600    # Ban duration (seconds)
findtime = 600    # Time window (seconds)
```

### Add Custom IP Blocks

**Temporary (via cache):**
- IPs are automatically blocked by middleware
- Blocks expire after configured time

**Permanent (via environment):**
```env
BLOCKED_IPS=ip1,ip2,ip3
```

## 🚨 Security Best Practices

### ✅ DO:
- ✅ Use SSH keys instead of passwords
- ✅ Change default SSH port (optional)
- ✅ Regularly review blocked IPs
- ✅ Monitor security logs
- ✅ Keep firewall rules updated
- ✅ Use Cloudflare for additional protection
- ✅ Enable 2FA for admin accounts

### ❌ DON'T:
- ❌ Expose database ports publicly
- ❌ Use weak passwords
- ❌ Disable firewall for "testing"
- ❌ Allow root SSH login with password
- ❌ Ignore security alerts
- ❌ Share admin credentials

## 📊 Firewall Statistics

### View Attack Statistics

```bash
# Count blocked IPs
fail2ban-client get sshd banned | wc -l

# View recent blocks
grep "Ban" /var/log/fail2ban.log | tail -20

# Check rate limit hits
grep "rate_limit" /opt/dice_game/backend/logs/django.log
```

## 🔄 Maintenance

### Weekly Tasks:
- Review blocked IPs
- Check security logs
- Update firewall rules if needed

### Monthly Tasks:
- Review Fail2Ban configuration
- Update blocked IP list
- Check for new attack patterns

### Quarterly Tasks:
- Security audit
- Review and update firewall rules
- Test firewall effectiveness

## 🆘 Troubleshooting

### Problem: Can't access admin panel
**Solution**: Check `ADMIN_WHITELIST_IPS` - your IP might not be whitelisted

### Problem: Legitimate IP blocked
**Solution**: 
```bash
./scripts/block_ip.sh unblock <IP>
fail2ban-client set sshd unbanip <IP>
```

### Problem: Too many false positives
**Solution**: Increase `maxretry` in Fail2Ban config or adjust rate limits

### Problem: Firewall blocking legitimate traffic
**Solution**: Check UFW rules: `ufw status verbose` and adjust as needed

## 📞 Emergency Procedures

### If Under Attack:

1. **Immediate Actions**:
   ```bash
   # Block attacking IP
   ./scripts/block_ip.sh block <ATTACKER_IP>
   
   # Enable Fail2Ban
   fail2ban-client start
   
   # Check logs
   tail -f /var/log/fail2ban.log
   ```

2. **Enable Cloudflare "Under Attack Mode"**:
   - Login to Cloudflare dashboard
   - Enable "Under Attack Mode"
   - This adds extra protection layer

3. **Contact Hosting Provider**:
   - Report DDoS attacks
   - Request IP blocking at network level

## 🎯 Protection Summary

Your server now has **5 layers of firewall protection**:

1. ✅ **Application Firewall** - IP blocking, rate limiting, attack detection
2. ✅ **System Firewall (UFW)** - Port blocking, connection limiting
3. ✅ **Fail2Ban** - Automatic IP banning
4. ✅ **System Hardening** - Kernel-level protection
5. ✅ **Docker Security** - Network isolation

**Result**: Your server and accounts are protected by multiple independent firewall layers!

---

**Last Updated**: February 2026
**Security Level**: Maximum Protection ✅
