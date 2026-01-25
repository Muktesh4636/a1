"""
WSGI config for dice_game project.
"""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dice_game.settings')

application = get_wsgi_application()








