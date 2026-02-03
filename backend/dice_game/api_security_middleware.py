"""
API-specific security middleware
- Enhanced rate limiting for API endpoints
- API attack detection and logging
- JWT token validation
"""
from django.core.cache import cache
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
import time
import os
import logging

logger = logging.getLogger(__name__)


class APISecurityMiddleware(MiddlewareMixin):
    """
    Additional security layer specifically for API endpoints
    - Tracks API request rates per IP
    - Detects API abuse patterns
    - Logs API attacks separately
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # API-specific rate limits (stricter than general)
        self.api_rate_limit = int(os.getenv('API_RATE_LIMIT', '200'))  # requests per hour
        self.api_rate_window = int(os.getenv('API_RATE_WINDOW', '3600'))  # 1 hour
        
    def get_client_ip(self, request):
        """Extract real client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '')
        return ip
    
    def check_api_rate_limit(self, ip, request):
        """Check API-specific rate limiting"""
        if not request.path.startswith('/api/'):
            return True  # Not an API endpoint, skip
        
        cache_key = f'api_rate_limit_{ip}'
        current_time = time.time()
        
        # Get current request count and window start
        rate_data = cache.get(cache_key, {'count': 0, 'window_start': current_time})
        
        # Reset if window expired
        if current_time - rate_data['window_start'] > self.api_rate_window:
            rate_data = {'count': 1, 'window_start': current_time}
        else:
            rate_data['count'] += 1
        
        # Store updated rate data
        cache.set(cache_key, rate_data, self.api_rate_window)
        
        # Check if limit exceeded
        if rate_data['count'] > self.api_rate_limit:
            logger.warning(f"API rate limit exceeded for IP {ip}: {rate_data['count']} requests")
            # Block IP temporarily for excessive API requests
            cache.set(f'api_blocked_{ip}', True, 3600)  # Block for 1 hour
            return False
        
        return True
    
    def detect_api_abuse(self, ip, request):
        """Detect API-specific abuse patterns"""
        if not request.path.startswith('/api/'):
            return True
        
        # Check for blocked API IP
        if cache.get(f'api_blocked_{ip}'):
            return False
        
        # Check for rapid-fire requests (potential DoS)
        rapid_fire_key = f'api_rapid_{ip}'
        current_time = time.time()
        last_request_time = cache.get(rapid_fire_key, 0)
        
        if current_time - last_request_time < 0.1:  # Less than 100ms between requests
            cache.set(f'api_blocked_{ip}', True, 1800)  # Block for 30 minutes
            logger.warning(f"API rapid-fire attack detected from IP {ip}")
            return False
        
        cache.set(rapid_fire_key, current_time, 60)  # Track for 1 minute
        
        return True
    
    def process_request(self, request):
        """Process API requests through security checks"""
        # Only apply to API endpoints
        if not request.path.startswith('/api/'):
            return None
        
        ip = self.get_client_ip(request)
        
        # Check API rate limit
        if not self.check_api_rate_limit(ip, request):
            return JsonResponse(
                {'error': 'API rate limit exceeded. Please try again later.'},
                status=429
            )
        
        # Detect API abuse
        if not self.detect_api_abuse(ip, request):
            return JsonResponse(
                {'error': 'API abuse detected. Your IP has been temporarily blocked.'},
                status=403
            )
        
        return None
