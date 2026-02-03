"""
WSGI config for dice_game project.
SECURITY: Modified to hide server information
"""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dice_game.settings')

application = get_wsgi_application()

# SECURITY: Remove server identification
if hasattr(application, '__call__'):
    # Wrap application to remove server headers
    original_call = application.__call__
    
    def wrapped_call(environ, start_response):
        def custom_start_response(status, headers, exc_info=None):
            # Filter out server identification headers
            filtered_headers = []
            headers_to_hide = ['server', 'x-powered-by', 'x-django-version']
            for header, value in headers:
                if header.lower() not in headers_to_hide:
                    filtered_headers.append((header, value))
            return start_response(status, filtered_headers, exc_info)
        
        return original_call(environ, custom_start_response)
    
    application.__call__ = wrapped_call
