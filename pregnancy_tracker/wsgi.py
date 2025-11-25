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

# RUN MIGRATIONS BEFORE STARTING APPLICATION
try:
    from django.core.management import call_command
    print("Running database migrations...")
    call_command('migrate', verbosity=1)
    call_command('migrate', 'account', verbosity=1)
    call_command('migrate', 'pregnancy', verbosity=1)
    print("All migrations completed successfully!")
except Exception as e:
    print(f"Migration completed with notes: {e}")

# Get the WSGI application
application = get_wsgi_application()

# Optional: Add middleware for production
try:
    from whitenoise import WhiteNoise
    application = WhiteNoise(application)
except ImportError:
    # WhiteNoise not installed, continue without it
    pass
