"""
WSGI config for LindaMama project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see:
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pregnancy_tracker.settings')

# Get the WSGI application
application = get_wsgi_application()

# Optional: Add middleware for production
try:
    from whitenoise import WhiteNoise
    application = WhiteNoise(application)
except ImportError:
    # WhiteNoise not installed, continue without it
    pass
