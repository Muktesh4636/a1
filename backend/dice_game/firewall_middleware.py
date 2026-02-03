"""
Multi-layer firewall middleware for comprehensive protection
- IP blocking and whitelisting
- Rate limiting per IP
- Geographic blocking (optional)
- Brute force detection
"""
from django.core.cache import cache
from django.http import HttpResponseForbidden, HttpResponseTooManyRequests
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
import time
import os


class MultiLayerFirewallMiddleware(MiddlewareMixin):
    """
    Application-level firewall with multiple protection layers:
    1. IP Whitelist/Blacklist
    2. Rate limiting per IP
    3. Brute force detection
    4. Suspicious activity blocking
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Get blocked IPs from environment (comma-separated)
        self.blocked_ips = set(
            ip.strip() for ip in os.getenv('BLOCKED_IPS', '').split(',') if ip.strip()
        )
        # Get whitelisted IPs for admin (comma-separated)
        self.admin_whitelist = set(
            ip.strip() for ip in os.getenv('ADMIN_WHITELIST_IPS', '').split(',') if ip.strip()
        )
        # Rate limit settings
        self.rate_limit_requests = int(os.getenv('RATE_LIMIT_REQUESTS', '100'))
        self.rate_limit_window = int(os.getenv('RATE_LIMIT_WINDOW', '60'))  # seconds
        # Brute force protection settings
        self.brute_force_threshold = int(os.getenv('BRUTE_FORCE_THRESHOLD', '50'))  # 50 failed attempts
        self.brute_force_ban_time = int(os.getenv('BRUTE_FORCE_BAN_TIME', '7200'))  # 2 hours
        
    def get_client_ip(self, request):
        """Extract real client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '')
        return ip
    
    def check_ip_blacklist(self, ip):
        """Check if IP is in blacklist"""
        # Check environment variable blacklist
        if ip in self.blocked_ips:
            return True
        
        # Check cache for dynamically blocked IPs
        if cache.get(f'blocked_ip_{ip}'):
            return True
        
        return False
    
    def check_ip_whitelist(self, request, ip):
        """Check if IP needs whitelist (admin panel)"""
        # Only check whitelist for admin panel
        if not request.path.startswith('/game-admin/'):
            return True
        
        # If whitelist is empty, allow all (backward compatible)
        if not self.admin_whitelist:
            return True
        
        # Check if IP is whitelisted
        return ip in self.admin_whitelist
    
    def check_rate_limit(self, ip):
        """Check rate limiting per IP"""
        cache_key = f'rate_limit_{ip}'
        current_time = time.time()
        
        # Get current request count and window start
        rate_data = cache.get(cache_key, {'count': 0, 'window_start': current_time})
        
        # Reset if window expired
        if current_time - rate_data['window_start'] > self.rate_limit_window:
            rate_data = {'count': 1, 'window_start': current_time}
        else:
            rate_data['count'] += 1
        
        # Store updated rate data
        cache.set(cache_key, rate_data, self.rate_limit_window)
        
        # Check if limit exceeded
        if rate_data['count'] > self.rate_limit_requests:
            # Block IP temporarily for excessive requests
            cache.set(f'blocked_ip_{ip}', True, 3600)  # Block for 1 hour
            return False
        
        return True
    
    def detect_brute_force(self, ip, request):
        """Detect and block brute force attempts"""
        # Track failed login attempts
        if request.path == '/game-admin/login/' and request.method == 'POST':
            failed_attempts_key = f'failed_logins_{ip}'
            failed_attempts = cache.get(failed_attempts_key, 0)
            
            # Check if password was wrong (this will be set by login view)
            # For now, we'll track all POST requests to login
            failed_attempts += 1
            cache.set(failed_attempts_key, failed_attempts, 900)  # 15 minutes
            
            # Block if too many failed attempts (configurable threshold)
            if failed_attempts >= self.brute_force_threshold:
                cache.set(f'blocked_ip_{ip}', True, self.brute_force_ban_time)
                return False
        
        return True
    
    def detect_suspicious_activity(self, ip, request):
        """Detect suspicious patterns"""
        suspicious_patterns = [
            '/admin/',  # Django admin (should use /game-admin/)
            '/wp-admin/',  # WordPress (not used)
            '/phpmyadmin/',  # phpMyAdmin (not used)
            '/.env',  # Environment file access
            '/config.php',  # Config file access
            '/wp-config.php',  # WordPress config
            'SELECT',  # SQL injection attempt
            'UNION',  # SQL injection attempt
            '<script>',  # XSS attempt
            '../',  # Path traversal
        ]
        
        request_path = request.path.lower()
        request_body = ''
        
        if request.method == 'POST':
            try:
                request_body = str(request.body).lower()
            except:
                pass
        
        for pattern in suspicious_patterns:
            if pattern.lower() in request_path or pattern.lower() in request_body:
                # Log suspicious activity
                cache.set(f'suspicious_{ip}', True, 3600)
                # Block IP temporarily
                cache.set(f'blocked_ip_{ip}', True, 1800)  # Block for 30 minutes
                return False
        
        return True
    
    def process_request(self, request):
        """Process request through firewall layers"""
        ip = self.get_client_ip(request)
        
        # Layer 1: Check blacklist
        if self.check_ip_blacklist(ip):
            return HttpResponseForbidden(
                '<h1>403 Forbidden</h1><p>Your IP address has been blocked.</p>',
                content_type='text/html'
            )
        
        # Layer 2: Check whitelist for admin panel
        if not self.check_ip_whitelist(request, ip):
            return HttpResponseForbidden(
                '<h1>403 Forbidden</h1><p>Access denied. Your IP is not whitelisted.</p>',
                content_type='text/html'
            )
        
        # Layer 3: Rate limiting
        if not self.check_rate_limit(ip):
            return HttpResponseTooManyRequests(
                '<h1>429 Too Many Requests</h1><p>Rate limit exceeded. Please try again later.</p>',
                content_type='text/html'
            )
        
        # Layer 4: Brute force detection
        if not self.detect_brute_force(ip, request):
            return HttpResponseForbidden(
                '<h1>403 Forbidden</h1><p>Too many failed login attempts. IP blocked temporarily.</p>',
                content_type='text/html'
            )
        
        # Layer 5: Suspicious activity detection
        if not self.detect_suspicious_activity(ip, request):
            return HttpResponseForbidden(
                '<h1>403 Forbidden</h1><p>Suspicious activity detected. Access denied.</p>',
                content_type='text/html'
            )
        
        # All checks passed
        return None
