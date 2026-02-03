"""
Cloudflare IP verification middleware
Only allows requests from Cloudflare IPs, blocks direct access to real server IP
Also prevents domain-based tracing
"""
from django.http import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
import os
import time


class CloudflareOnlyMiddleware(MiddlewareMixin):
    """
    Middleware to ONLY allow requests from Cloudflare
    Blocks direct access to real server IP
    """
    
    # Cloudflare IP ranges (IPv4) - Updated list
    CLOUDFLARE_IPS = [
        '173.245.48.0/20', '103.21.244.0/22', '103.22.200.0/22',
        '103.31.4.0/22', '141.101.64.0/18', '108.162.192.0/18',
        '190.93.240.0/20', '188.114.96.0/20', '197.234.240.0/22',
        '198.41.128.0/17', '162.158.0.0/15', '104.16.0.0/13',
        '104.24.0.0/14', '172.64.0.0/13', '131.0.72.0/22',
        '103.21.244.0/22', '103.22.200.0/22', '103.31.4.0/22',
        '141.101.64.0/18', '108.162.192.0/18', '190.93.240.0/20',
        '188.114.96.0/20', '197.234.240.0/22', '198.41.128.0/17',
        '162.158.0.0/15', '104.16.0.0/13', '104.24.0.0/14',
        '172.64.0.0/13', '131.0.72.0/22',
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Check if Cloudflare-only mode is enabled
        self.enforce_cloudflare = os.getenv('ENFORCE_CLOUDFLARE_ONLY', 'False') == 'True'
    
    def ip_in_range(self, ip, ip_range):
        """Check if IP is in CIDR range"""
        try:
            from ipaddress import ip_address, ip_network
            return ip_address(ip) in ip_network(ip_range)
        except:
            return False
    
    def get_real_ip(self, request):
        """Get real client IP from Cloudflare headers"""
        # Cloudflare sends real IP in CF-Connecting-IP header
        cf_ip = request.META.get('HTTP_CF_CONNECTING_IP')
        if cf_ip:
            return cf_ip
        
        # Fallback to X-Forwarded-For (first IP)
        x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
        if x_forwarded:
            return x_forwarded.split(',')[0].strip()
        
        return request.META.get('REMOTE_ADDR', '')
    
    def is_cloudflare_ip(self, ip):
        """Check if request came from Cloudflare"""
        for cf_range in self.CLOUDFLARE_IPS:
            if self.ip_in_range(ip, cf_range):
                return True
        return False
    
    def process_request(self, request):
        """Block direct access to real server IP and prevent domain tracing"""
        if not self.enforce_cloudflare:
            return None
        
        # Get the IP that connected to our server
        connecting_ip = request.META.get('REMOTE_ADDR', '')
        
        # Check if request came from Cloudflare
        if not self.is_cloudflare_ip(connecting_ip):
            # Direct access to real IP - BLOCK IT
            # Also log the attempt to detect domain tracing attempts
            cache_key = f'direct_access_attempt_{connecting_ip}'
            attempts = cache.get(cache_key, 0) + 1
            cache.set(cache_key, attempts, 3600)
            
            # If multiple direct access attempts, permanently block
            if attempts >= 3:
                from .attack_detection import AttackDetector
                AttackDetector.block_ip_permanently(connecting_ip)
            
            return HttpResponseForbidden(
                '<h1>403 Forbidden</h1><p>Direct access not allowed. Please use the domain name.</p>',
                content_type='text/html'
            )
        
        # Request came through Cloudflare - allow it
        # Real client IP is in CF-Connecting-IP header (from Cloudflare)
        # This prevents tracing back to domain registrant
        return None
