"""
Django settings for pregnancy_tracker project.
Ready for Render deployment.
"""

import os
from pathlib import Path
from django.contrib.messages import constants as messages
from decouple import config
import dj_database_url  # Added for Render PostgreSQL database

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------
# SECURITY
# ---------------------------------------------------------------------
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-this-in-production-!')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = ['.onrender.com', 'localhost', '127.0.0.1']

# ---------------------------------------------------------------------
# APPLICATIONS
# ---------------------------------------------------------------------
INSTALLED_APPS = [
    # Default Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    # Third-party apps
    'crispy_forms',
    'crispy_bootstrap5',
    'rest_framework',
    'django_filters',

    # Local apps
    'pregnancy.apps.PregnancyConfig',
]

# ---------------------------------------------------------------------
# MIDDLEWARE
# ---------------------------------------------------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Handles static files in production
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',   # For Swahili/English translation support
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ---------------------------------------------------------------------
# URL & WSGI
# ---------------------------------------------------------------------
ROOT_URLCONF = 'pregnancy_tracker.urls'
WSGI_APPLICATION = 'pregnancy_tracker.wsgi.application'

# ---------------------------------------------------------------------
# TEMPLATES
# ---------------------------------------------------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
            BASE_DIR / 'pregnancy' / 'templates',
        ],
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

# ---------------------------------------------------------------------
# DATABASE
# ---------------------------------------------------------------------
# Default: SQLite (for local development)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Use PostgreSQL in production (Render)
if not DEBUG:
    DATABASES['default'] = dj_database_url.config(
        default=config('DATABASE_URL', default=''),
        conn_max_age=600,
        ssl_require=True
    )

# ---------------------------------------------------------------------
# AUTHENTICATION
# ---------------------------------------------------------------------
AUTH_USER_MODEL = 'pregnancy.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ---------------------------------------------------------------------
# INTERNATIONALIZATION
# ---------------------------------------------------------------------
LANGUAGE_CODE = 'en'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True

LANGUAGES = [
    ('en', 'English'),
    ('sw', 'Swahili'),
]
LOCALE_PATHS = [BASE_DIR / 'locale']

# ---------------------------------------------------------------------
# STATIC & MEDIA FILES
# ---------------------------------------------------------------------
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
    BASE_DIR / 'pregnancy' / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ---------------------------------------------------------------------
# LOGIN/LOGOUT REDIRECTS
# ---------------------------------------------------------------------
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'home'
LOGIN_URL = 'login'

# ---------------------------------------------------------------------
# MESSAGES
# ---------------------------------------------------------------------
MESSAGE_TAGS = {
    messages.DEBUG: 'secondary',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}

# ---------------------------------------------------------------------
# CRISPY FORMS
# ---------------------------------------------------------------------
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

# ---------------------------------------------------------------------
# EMAIL CONFIGURATION
# ---------------------------------------------------------------------
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@localhost')
SERVER_EMAIL = config('SERVER_EMAIL', default='admin@localhost')

# ---------------------------------------------------------------------
# DJANGO REST FRAMEWORK
# ---------------------------------------------------------------------
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticated'],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}

# ---------------------------------------------------------------------
# FILE UPLOADS
# ---------------------------------------------------------------------
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024

# ---------------------------------------------------------------------
# SESSION CONFIGURATION
# ---------------------------------------------------------------------
SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_SAVE_EVERY_REQUEST = True

# ---------------------------------------------------------------------
# SECURITY CONFIGURATION (for production)
# ---------------------------------------------------------------------
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# ---------------------------------------------------------------------
# LOGGING
# ---------------------------------------------------------------------
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {'format': '{levelname} {asctime} {module} {message}', 'style': '{'},
        'simple': {'format': '{levelname} {message}', 'style': '{'},
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': LOGS_DIR / 'django.log',
            'formatter': 'verbose',
        },
        'console': {'level': 'DEBUG', 'class': 'logging.StreamHandler', 'formatter': 'simple'},
    },
    'root': {'handlers': ['console'], 'level': 'INFO'},
    'loggers': {
        'django': {'handlers': ['file', 'console'], 'level': 'INFO', 'propagate': False},
        'pregnancy': {'handlers': ['file', 'console'], 'level': 'DEBUG', 'propagate': False},
    },
}

# ---------------------------------------------------------------------
# APP CUSTOM CONFIG
# ---------------------------------------------------------------------
PREGNANCY_TRACKER_CONFIG = {
    'APP_NAME': 'Linda Mama Pregnancy App',
    'APP_VERSION': '1.0.0',
    'SUPPORT_EMAIL': 'support@localhost',
    'SUPPORT_PHONE': '+254700000000',
    'MAX_APPOINTMENTS_PER_DAY': 5,
    'EMERGENCY_RESPONSE_TIMEOUT_MINUTES': 30,
    'DEFAULT_PREGNANCY_WEEKS': 40,
}

# ---------------------------------------------------------------------
# CACHING
# ---------------------------------------------------------------------
if not DEBUG:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': config('REDIS_URL', default='redis://127.0.0.1:6379'),
        }
    }
else:
    CACHES = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}
