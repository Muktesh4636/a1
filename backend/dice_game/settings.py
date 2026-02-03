"""
Django settings for dice_game project.
"""

from pathlib import Path
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-change-this-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False') == 'True'  # Default to False for production

# Security: Only allow specific hosts
ALLOWED_HOSTS_STR = os.getenv('ALLOWED_HOSTS', 'gunduata.online,www.gunduata.online,72.61.254.71')
ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS_STR.split(',') if host.strip()]


# Application definition

INSTALLED_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'channels',
    # Local apps
    'accounts',
    'game',
]

# OCR Settings
# You must install tesseract-ocr on your system for this to work
# macOS: brew install tesseract
# Ubuntu: sudo apt-get install tesseract-ocr
# Windows: Download installer from GitHub
TESSERACT_CMD = os.getenv('TESSERACT_CMD', '/opt/homebrew/bin/tesseract')

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# SECURITY: Production security settings
if not DEBUG:
    # HTTPS/SSL Settings
    SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'False') == 'True'
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    
    # HSTS (HTTP Strict Transport Security)
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    # Additional security headers
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    
    # CSRF trusted origins for production
    CSRF_TRUSTED_ORIGINS = [
        'https://gunduata.online',
        'https://www.gunduata.online',
        'http://72.61.254.71',  # Remove this when HTTPS is enabled
    ]
    
    # Session security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    CSRF_COOKIE_HTTPONLY = True
    CSRF_COOKIE_SAMESITE = 'Lax'
    
    # Password reset timeout (in seconds)
    PASSWORD_RESET_TIMEOUT = 3600  # 1 hour

ROOT_URLCONF = 'dice_game.urls'

# Custom error handlers
handler404 = 'dice_game.views.custom_404_handler'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'dice_game.wsgi.application'
ASGI_APPLICATION = 'dice_game.asgi.application'


# Database
# Use SQLite for development (no PostgreSQL required)
USE_SQLITE = os.getenv('USE_SQLITE', 'True') == 'True'

if USE_SQLITE:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    # PostgreSQL configuration (for production)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME', 'dice_game'),
            'USER': os.getenv('DB_USER', 'postgres'),
            'PASSWORD': os.getenv('DB_PASSWORD', 'postgres'),
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '5432'),
            'CONN_MAX_AGE': 600,  # 10 minutes - connection pooling
            'OPTIONS': {
                'connect_timeout': 10,  # Connection timeout
                'options': '-c statement_timeout=30000',  # 30 second statement timeout
            },
        }
    }


# Password validation - SECURITY: Strong password requirements
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,  # Minimum 8 characters
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static' / 'react',
]
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# React app build directory
REACT_BUILD_DIR = BASE_DIR / 'static' / 'react'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# REST Framework - SECURITY: Rate limiting and throttling
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    # Rate limiting to prevent abuse
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',  # Anonymous users: 100 requests per hour
        'user': '1000/hour',  # Authenticated users: 1000 requests per hour
        'login': '5/minute',  # Login attempts: 5 per minute
        'bet': '60/minute',  # Betting: 60 bets per minute
    }
}

# JWT Settings - SECURITY: Shorter token lifetimes
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),  # Reduced from 24h to 1h
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# CORS Settings - SECURITY: Restrict to specific origins
CORS_ALLOWED_ORIGINS_STR = os.getenv(
    'CORS_ALLOWED_ORIGINS',
    'https://gunduata.online,https://www.gunduata.online,http://localhost:5173,http://localhost:3000'
)
CORS_ALLOWED_ORIGINS = [
    origin.strip() for origin in CORS_ALLOWED_ORIGINS_STR.split(',') if origin.strip()
]

# Only allow credentials from trusted origins
CORS_ALLOW_CREDENTIALS = True

# CORS Security: Block all other origins
CORS_ALLOW_ALL_ORIGINS = False

# Redis Configuration
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)

# Redis Connection Pool (for efficient connection reuse)
# IMPORTANT: This is NOT 1 connection per user!
# - Connections are SHARED and REUSED across all users
# - Each operation borrows a connection, uses it, then returns it to the pool
# - Typical ratio: 1 Redis connection can serve 100-1000 concurrent users
# - Pool size should be: (expected concurrent users / 100) + buffer
try:
    import redis
    # Calculate pool size based on expected users
    # Default: 5000 connections (can handle ~500K concurrent users)
    # For 10M users, use Redis Cluster instead (see SCALABILITY_ANALYSIS.md)
    REDIS_POOL_SIZE = int(os.getenv('REDIS_POOL_SIZE', '5000'))
    
    # Create connection pool for Redis
    pool_kwargs = {
        'host': REDIS_HOST,
        'port': REDIS_PORT,
        'db': REDIS_DB,
        'max_connections': REDIS_POOL_SIZE,
        'decode_responses': True,
        'socket_connect_timeout': 5,
        'socket_timeout': 5,
        'retry_on_timeout': True,
    }
    
    # Add password if provided
    if REDIS_PASSWORD:
        pool_kwargs['password'] = REDIS_PASSWORD
    
    REDIS_POOL = redis.ConnectionPool(**pool_kwargs)
    
    # Test Redis connection
    redis_test = redis.Redis(connection_pool=REDIS_POOL)
    redis_test.ping()
    redis_test.close()
    USE_REDIS = True
    USE_REDIS_CHANNELS = True
except Exception as e:
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(f"Redis not available: {e}")
    USE_REDIS = False
    USE_REDIS_CHANNELS = False
    REDIS_POOL = None

# Channels (WebSocket)
# Use Redis channel layer (required for game timer to broadcast to WebSocket consumers)
# In-memory layer only works within same process, but game timer runs separately
if USE_REDIS_CHANNELS:
    # Redis configuration (required for cross-process communication)
    # channels_redis requires URL format for authentication, not separate password key
    if REDIS_PASSWORD:
        # Format: redis://:password@host:port/db
        redis_url = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
        channel_config = {
            "hosts": [redis_url],
            "capacity": 5000,  # Increased: Messages per channel (prevents message drops)
            "expiry": 60,  # Increased: Message expiry in seconds (prevents premature expiry)
            "group_expiry": 31536000,  # Group expiry (1 year) - prevents connections from being removed from group
        }
    else:
        channel_config = {
            "hosts": [(REDIS_HOST, REDIS_PORT)],
            "capacity": 5000,  # Increased: Messages per channel (prevents message drops)
            "expiry": 60,  # Increased: Message expiry in seconds (prevents premature expiry)
            "group_expiry": 31536000,  # Group expiry (1 year) - prevents connections from being removed from group
        }
    
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': channel_config,
        },
    }
else:
    # Fallback to in-memory (only works within same process)
    # Note: Game timer won't be able to broadcast if using this
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels.layers.InMemoryChannelLayer',
        },
    }

# Game Settings
GAME_SETTINGS = {
    'BETTING_DURATION': 30,  # seconds (0-30s) - Betting open
    'RESULT_SELECTION_DURATION': 20,  # seconds (31-50s) - Betting closed, waiting for dice roll
    'RESULT_DISPLAY_DURATION': 20,  # seconds (51-70s) - Show dice result
    'TOTAL_ROUND_DURATION': 70,  # seconds (70 seconds total)
     'DICE_ROLL_TIME': 19,  # seconds - Time before dice result when warning is sent   
    'BETTING_CLOSE_TIME': 30,  # seconds - Stop taking bets (0-30s betting open)
    'DICE_RESULT_TIME': 51,  # seconds - Auto-roll dice if not set manually
    'RESULT_ANNOUNCE_TIME': 51,  # seconds - Announce result
    'ROUND_END_TIME': 80,  # seconds - End round and start new one
    'CHIP_VALUES': [10, 20, 50, 100],
    'PAYOUT_RATIOS': {
        1: 6.0,  # If you bet on 1 and it comes, you get 6x
        2: 6.0,
        3: 6.0,
        4: 6.0,
        5: 6.0,
        6: 6.0,
    },
}

# Redis Settings
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))

