from django.http import HttpResponse, JsonResponse, FileResponse
from django.conf import settings
from django.views.decorators.cache import never_cache
from rest_framework.decorators import api_view
from rest_framework.response import Response
import os


def api_root(request):
    """API root endpoint that lists available API endpoints"""
    base_url = request.build_absolute_uri('/')
    api_data = {
        'name': 'Gundu ata API',
        'version': '1.0',
        'description': 'REST API for Gundu ata application',
        'endpoints': {
            'auth': {
                'base_url': f'{base_url}api/auth/',
                'endpoints': {
                    'register': f'{base_url}api/auth/register/',
                    'login': f'{base_url}api/auth/login/',
                    'profile': f'{base_url}api/auth/profile/',
                    'wallet': f'{base_url}api/auth/wallet/',
                    'transactions': f'{base_url}api/auth/transactions/',
                }
            },
            'game': {
                'base_url': f'{base_url}api/game/',
                'endpoints': {
                    'round': f'{base_url}api/game/round/',
                    'bet': f'{base_url}api/game/bet/',
                    'bets': f'{base_url}api/game/bets/',
                }
            }
        },
        'admin': {
            'game_admin': f'{base_url}game-admin/dashboard/',
        }
    }
    return JsonResponse(api_data, json_dumps_params={'indent': 2})


def root_status(request):
    """Simple landing page so / shows helpful links instead of 404."""
    admin_url = request.build_absolute_uri('/admin/')
    dashboard_url = request.build_absolute_uri('/game-admin/dashboard/')
    api_url = request.build_absolute_uri('/api/')

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <title>Gundu ata Backend</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                background: #f5f7fb;
                color: #1f2933;
                margin: 0;
                padding: 40px 20px;
            }}
            .container {{
                max-width: 720px;
                margin: 0 auto;
                background: #fff;
                border-radius: 12px;
                box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
                padding: 32px 40px;
            }}
            h1 {{
                margin-top: 0;
                font-size: 32px;
            }}
            p {{
                line-height: 1.6;
            }}
            a.button {{
                display: inline-block;
                margin: 12px 12px 0 0;
                padding: 12px 18px;
                border-radius: 8px;
                background: #6366f1;
                color: #fff;
                text-decoration: none;
                font-weight: 600;
            }}
            .links {{
                margin-top: 24px;
            }}
            code {{
                background: #eef2ff;
                padding: 3px 6px;
                border-radius: 4px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Gundu ata Backend</h1>
            <p>
                The Django backend is running. Use the links below to access the admin
                panel, custom game dashboard, or REST API.
            </p>
            <div class="links">
                <a class="button" href="{dashboard_url}">Game Admin Dashboard</a>
                <a class="button" href="{api_url}">API Root</a>
            </div>
            <p style="margin-top:24px;">
                Frontend (React/Vite) runs separately on <code>npm run dev</code> (default <code>http://localhost:5173</code>).
            </p>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html)


@never_cache
def serve_react_app(request, path=''):
    """Serve React app - serves index.html for all routes except API/admin"""
    react_build_dir = getattr(settings, 'REACT_BUILD_DIR', None)
    
    if not react_build_dir or not os.path.exists(react_build_dir):
        # If React build doesn't exist, return a helpful message
        return HttpResponse("""
        <html>
            <head><title>React App Not Built</title></head>
            <body style="font-family: sans-serif; padding: 40px; text-align: center;">
                <h1>React App Not Built</h1>
                <p>Please run <code>npm run build</code> to build the React app.</p>
                <p>Then restart the Django server.</p>
            </body>
        </html>
        """, status=503)
    
    # Get the full path from the request
    request_path = request.path.lstrip('/')
    
    # If requesting a static file (JS, CSS, images, etc.), serve it
    if request_path and '.' in request_path:
        # Check in assets directory first (Vite build structure)
        file_path = os.path.join(react_build_dir, request_path)
        if not os.path.exists(file_path):
            # Try assets directory
            file_path = os.path.join(react_build_dir, 'assets', os.path.basename(request_path))
        
        if os.path.exists(file_path) and os.path.isfile(file_path):
            # Determine content type
            content_type = 'application/octet-stream'
            if file_path.endswith('.js'):
                content_type = 'application/javascript'
            elif file_path.endswith('.css'):
                content_type = 'text/css'
            elif file_path.endswith('.png'):
                content_type = 'image/png'
            elif file_path.endswith('.jpg') or file_path.endswith('.jpeg'):
                content_type = 'image/jpeg'
            elif file_path.endswith('.svg'):
                content_type = 'image/svg+xml'
            
            return FileResponse(open(file_path, 'rb'), content_type=content_type)
    
    # For all other routes, serve index.html (React Router will handle routing)
    index_path = os.path.join(react_build_dir, 'index.html')
    if os.path.exists(index_path):
        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return HttpResponse(content, content_type='text/html')
    
    return HttpResponse("React app index.html not found", status=404)


def custom_404_handler(request, exception):
    """Custom 404 handler that returns JSON for API requests"""
    if request.path.startswith('/api/'):
        return JsonResponse({
            'error': 'Not Found',
            'detail': f'The requested resource "{request.path}" was not found on this server.',
            'path': request.path
        }, status=404)
    # For non-API requests, return the default HTML 404
    from django.views.defaults import page_not_found
    return page_not_found(request, exception)






