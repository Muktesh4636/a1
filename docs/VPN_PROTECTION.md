# 🛡️ VPN-Resistant Protection

## How We Protect Against VPN Attacks

### The Problem
When attackers use VPNs, they can:
- Change IP addresses easily
- Bypass IP-based blocking
- Continue attacks with new IPs

### Our Solution: Multi-Layer VPN Protection

#### 1. **Device Fingerprinting** (Primary Defense)
We create a unique "fingerprint" from:
- Browser User-Agent
- Accept-Language headers
- Accept-Encoding headers
- Screen resolution (if available)
- Timezone (if available)
- Canvas fingerprint (if available)
- WebGL fingerprint (if available)

**Result**: Even if attacker changes VPN IP, we still identify their device!

#### 2. **Behavioral Tracking**
- Tracks attack patterns across different IPs
- Identifies same attacker using multiple VPN IPs
- Blocks device after 3 attacks (configurable)

#### 3. **VPN Pattern Detection**
- Detects when same IP is used by multiple devices
- Identifies VPN/proxy IPs automatically
- Applies stricter rate limits to VPN IPs

#### 4. **Multi-IP Tracking**
- Tracks all IPs used by same fingerprint
- Logs VPN IPs used by attackers
- Blocks all known VPN IPs from same attacker

### How It Works

```
Attacker uses VPN → Gets IP 1.2.3.4
├─ Attack detected → IP blocked
├─ Fingerprint created → abc123...
└─ Fingerprint tracked → 1 attack logged

Attacker switches VPN → Gets IP 5.6.7.8
├─ Same fingerprint detected → abc123...
├─ Attack detected → IP blocked
└─ Fingerprint tracked → 2 attacks logged

Attacker switches VPN again → Gets IP 9.10.11.12
├─ Same fingerprint detected → abc123...
├─ Attack detected → IP blocked
└─ Fingerprint tracked → 3 attacks → DEVICE PERMANENTLY BLOCKED
```

### What Gets Logged

**Fingerprint Log** (`fingerprint_attacks.log`):
```
2026-02-02 14:30:15 | Fingerprint: abc123... | IP: 1.2.3.4 | Type: sql_injection | BLOCKED
2026-02-02 14:35:22 | Fingerprint: abc123... | IP: 5.6.7.8 | Type: xss | BLOCKED
2026-02-02 14:40:10 | Fingerprint: abc123... | IP: 9.10.11.12 | Type: command_injection | BLOCKED
```

**Main Attack Log** (`attacks.log`):
```
2026-02-02 14:30:15 | IP: 1.2.3.4 | Type: sql_injection | Fingerprint: abc123... | User-Agent: Mozilla/5.0... | BLOCKED
```

### Viewing VPN Attacks

```bash
# View fingerprint-based attacks
./scripts/view_fingerprint_attacks.sh

# View all attacks (including fingerprints)
./scripts/view_attacks.sh
```

### Configuration

Set in `.env`:
```env
FINGERPRINT_BLOCK_THRESHOLD=3  # Block after 3 attacks
```

### Limitations

1. **Tor Browser**: May generate different fingerprints each time
   - **Solution**: We still track by attack patterns and rate limit

2. **Shared VPNs**: Multiple users sharing same VPN IP
   - **Solution**: We detect this pattern and apply stricter limits

3. **Browser Changes**: Attacker changes browser
   - **Solution**: We still track by IP patterns and attack signatures

### Best Practices

1. **Enable Cloudflare**: Hides your real IP
2. **Monitor Fingerprints**: Check `fingerprint_attacks.log` regularly
3. **Adjust Threshold**: Lower `FINGERPRINT_BLOCK_THRESHOLD` for stricter blocking
4. **Combine with IP Blocking**: Both systems work together

### Summary

✅ **VPN IP changes** → Still tracked by fingerprint  
✅ **Device fingerprint** → Permanent identifier  
✅ **Behavioral patterns** → Detected across IPs  
✅ **Multi-layer protection** → IP + Fingerprint + Behavior  

**Result**: Even with VPN, attackers get blocked after 3 attempts!
