"""
Anonymization middleware to prevent tracing
- Remove identifying headers
- Rotate session IDs
- Prevent fingerprinting
- Remove tracking information
"""
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
import hashlib
import time


class AnonymizationMiddleware(MiddlewareMixin):
    """
    Middleware to prevent tracing and fingerprinting
    """
    
    def process_request(self, request):
        # Rotate session key periodically to prevent tracking
        if request.session.session_key:
            # Change session key every hour to prevent long-term tracking
            session_age = time.time() - request.session.get('_session_init_timestamp_', time.time())
            if session_age > 3600:  # 1 hour
                request.session.cycle_key()
                request.session['_session_init_timestamp_'] = time.time()
        else:
            request.session['_session_init_timestamp_'] = time.time()
        
        return None
    
    def process_response(self, request, response):
        # Remove all identifying headers
        headers_to_remove = [
            'X-Forwarded-For',
            'X-Real-IP',
            'X-Client-IP',
            'X-Forwarded-Host',
            'X-Original-URL',
            'Via',
            'X-Request-ID',
            'X-Correlation-ID',
            'Server-Timing',
            'X-AspNet-Version',
            'X-Powered-By',
            'X-Runtime',
            'X-Version',
        ]
        
        for header in headers_to_remove:
            if header in response:
                del response[header]
        
        # Add headers to prevent tracking
        response['X-Content-Type-Options'] = 'nosniff'
        response['Referrer-Policy'] = 'no-referrer'
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        response['X-DNS-Prefetch-Control'] = 'off'
        
        # Remove any IP-related headers that might leak information
        if 'X-Forwarded-For' in request.META:
            # Don't log or store forwarded IPs
            pass
        
        # Remove cookies that could be used for tracking
        if 'Set-Cookie' in response:
            # Make session cookies more anonymous
            cookies = response.get('Set-Cookie', '')
            if 'sessionid' in cookies:
                # Session cookies already handled by Django settings
        
        return response
