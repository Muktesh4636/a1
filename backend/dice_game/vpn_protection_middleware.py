"""
VPN-Resistant Protection Middleware
- Behavioral fingerprinting (beyond IP addresses)
- Device/browser fingerprinting
- Attack pattern tracking across VPN IPs
- Session-based blocking
"""
from django.core.cache import cache
from django.http import JsonResponse, HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin
import hashlib
import json
import time
import os
import logging

logger = logging.getLogger(__name__)


class VPNProtectionMiddleware(MiddlewareMixin):
    """
    Protection against VPN-based attacks using:
    1. Behavioral fingerprinting
    2. Device fingerprinting
    3. Attack pattern tracking
    4. Session-based blocking
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.fingerprint_threshold = int(os.getenv('FINGERPRINT_BLOCK_THRESHOLD', '3'))  # Block after 3 attacks
        
    def create_fingerprint(self, request):
        """Create a unique fingerprint from request headers and behavior"""
        fingerprint_parts = []
        
        # User-Agent (browser/device info)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        fingerprint_parts.append(user_agent)
        
        # Accept headers (browser capabilities)
        accept_language = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
        accept_encoding = request.META.get('HTTP_ACCEPT_ENCODING', '')
        fingerprint_parts.append(accept_language)
        fingerprint_parts.append(accept_encoding)
        
        # Screen resolution (if available via JavaScript)
        screen_res = request.META.get('HTTP_X_SCREEN_RESOLUTION', '')
        fingerprint_parts.append(screen_res)
        
        # Timezone (if available)
        timezone = request.META.get('HTTP_X_TIMEZONE', '')
        fingerprint_parts.append(timezone)
        
        # Canvas fingerprint (if available)
        canvas_hash = request.META.get('HTTP_X_CANVAS_HASH', '')
        fingerprint_parts.append(canvas_hash)
        
        # WebGL fingerprint (if available)
        webgl_hash = request.META.get('HTTP_X_WEBGL_HASH', '')
        fingerprint_parts.append(webgl_hash)
        
        # Combine all parts and create hash
        fingerprint_string = '|'.join(fingerprint_parts)
        fingerprint_hash = hashlib.sha256(fingerprint_string.encode()).hexdigest()
        
        return fingerprint_hash
    
    def get_client_ip(self, request):
        """Extract client IP (VPN IP will be different each time)"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', '')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '')
        return ip
    
    def track_attack_by_fingerprint(self, fingerprint, ip, attack_type, request):
        """Track attacks by fingerprint (works even if IP changes via VPN)"""
        fingerprint_key = f'fingerprint_attacks_{fingerprint}'
        ip_key = f'ip_attacks_{ip}'
        
        # Get current attack count for this fingerprint
        fingerprint_attacks = cache.get(fingerprint_key, {'count': 0, 'ips': set(), 'types': []})
        fingerprint_attacks['count'] += 1
        fingerprint_attacks['ips'].add(ip)
        fingerprint_attacks['types'].append(attack_type)
        fingerprint_attacks['last_attack'] = time.time()
        
        # Store fingerprint attacks (permanent until cleared)
        cache.set(fingerprint_key, fingerprint_attacks, 31536000)  # 1 year
        
        # Also track IP attacks (for VPN IP detection)
        ip_attacks = cache.get(ip_key, {'count': 0, 'fingerprints': set()})
        ip_attacks['count'] += 1
        ip_attacks['fingerprints'].add(fingerprint)
        cache.set(ip_key, ip_attacks, 86400)  # 24 hours
        
        # Block fingerprint if threshold exceeded
        if fingerprint_attacks['count'] >= self.fingerprint_threshold:
            cache.set(f'blocked_fingerprint_{fingerprint}', True, 31536000)  # Permanent block
            logger.error(f"FINGERPRINT BLOCKED: {fingerprint[:16]}... | Attacks: {fingerprint_attacks['count']} | IPs used: {len(fingerprint_attacks['ips'])}")
            return True
        
        return False
    
    def detect_vpn_pattern(self, ip, fingerprint):
        """Detect if IP is likely a VPN (multiple fingerprints using same IP)"""
        ip_key = f'ip_attacks_{ip}'
        ip_data = cache.get(ip_key, {})
        
        if 'fingerprints' in ip_data and len(ip_data['fingerprints']) > 5:
            # Same IP used by many different fingerprints = likely VPN/proxy
            return True
        
        return False
    
    def check_fingerprint_block(self, fingerprint):
        """Check if fingerprint is blocked"""
        return cache.get(f'blocked_fingerprint_{fingerprint}', False)
    
    def process_request(self, request):
        """Process request through VPN-resistant protection"""
        ip = self.get_client_ip(request)
        fingerprint = self.create_fingerprint(request)
        
        # Check if fingerprint is blocked (works even if IP changes)
        if self.check_fingerprint_block(fingerprint):
            logger.warning(f"Blocked fingerprint attempted access: {fingerprint[:16]}... | IP: {ip}")
            return HttpResponseForbidden(
                '<h1>403 Forbidden</h1><p>Your device has been blocked due to suspicious activity.</p>',
                content_type='text/html'
            )
        
        # Check for VPN pattern (multiple devices using same IP)
        if self.detect_vpn_pattern(ip, fingerprint):
            # Rate limit VPN IPs more aggressively
            vpn_rate_key = f'vpn_rate_{ip}'
            vpn_requests = cache.get(vpn_rate_key, 0) + 1
            cache.set(vpn_rate_key, vpn_requests, 3600)
            
            if vpn_requests > 50:  # Lower threshold for VPN IPs
                logger.warning(f"VPN IP rate limit exceeded: {ip}")
                return HttpResponseTooManyRequests(
                    '<h1>429 Too Many Requests</h1><p>Rate limit exceeded for this IP.</p>',
                    content_type='text/html'
                )
        
        # Store fingerprint for tracking (if attack detected later)
        request._fingerprint = fingerprint
        request._fingerprint_ip = ip
        
        return None
    
    def process_response(self, request, response):
        """Track attacks after response is generated"""
        # Check if attack was detected (set by attack detection)
        if hasattr(request, '_attack_detected') and request._attack_detected:
            fingerprint = getattr(request, '_fingerprint', None)
            ip = getattr(request, '_fingerprint_ip', None)
            attack_type = getattr(request, '_attack_type', 'unknown')
            
            if fingerprint and ip:
                # Track attack by fingerprint (VPN-resistant)
                blocked = self.track_attack_by_fingerprint(fingerprint, ip, attack_type, request)
                
                if blocked:
                    logger.error(f"FINGERPRINT PERMANENTLY BLOCKED: {fingerprint[:16]}... | IP: {ip} | Type: {attack_type}")
        
        return response
