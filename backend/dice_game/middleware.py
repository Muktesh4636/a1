"""
Custom middleware to hide server information and prevent tracing
"""
from django.utils.deprecation import MiddlewareMixin


class HideServerInfoMiddleware(MiddlewareMixin):
    """
    Middleware to remove server identification headers and prevent tracing.
    Removes: Server, X-Powered-By, X-Django-Version, and other identifying headers.
    """
    
    def process_response(self, request, response):
        # Remove server identification headers
        headers_to_remove = [
            'Server',
            'X-Powered-By',
            'X-Django-Version',
            'X-Framework',
            'X-Application',
            'X-Runtime',
            'X-Version',
        ]
        
        for header in headers_to_remove:
            if header in response:
                del response[header]
        
        # Add headers to prevent fingerprinting
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Prevent information disclosure
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Remove any Django-specific headers that might leak info
        django_headers = [h for h in response.keys() if h.startswith('X-Django')]
        for header in django_headers:
            del response[header]
        
        return response
