"""
ASGI config for LindaMama project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see:
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
import django
from django.core.asgi import get_asgi_application

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pregnancy_tracker.settings')

# Initialize Django
django.setup()

# Get the default ASGI application
application = get_asgi_application()

# Optional: Add support for Django Channels (for WebSockets/real-time features)
try:
    from channels.routing import ProtocolTypeRouter, URLRouter
    from channels.auth import AuthMiddlewareStack
    from channels.security.websocket import AllowedHostsOriginValidator
    
    # Import your WebSocket routing if using Channels
    from apps.messaging import routing as messaging_routing
    from apps.pregnancy import routing as pregnancy_routing
    
    # Define WebSocket URL patterns
    websocket_urlpatterns = []
    
    # Add messaging WebSocket routes
    websocket_urlpatterns += messaging_routing.websocket_urlpatterns
    
    # Add pregnancy tracking WebSocket routes
    websocket_urlpatterns += pregnancy_routing.websocket_urlpatterns
    
    # Create the ASGI application with WebSocket support
    application = ProtocolTypeRouter({
        "http": application,
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(
                URLRouter(websocket_urlpatterns)
            )
        ),
    })
    
except ImportError:
    # Channels is not installed, use standard ASGI application
    print("Django Channels not installed. Running without WebSocket support.")
    pass

# Optional: Add additional ASGI middleware for production
try:
    from asgi_correlation_id import CorrelationIdMiddleware
    application = CorrelationIdMiddleware(application)
except ImportError:
    # Correlation ID middleware not installed
    pass

# Optional: Add security headers middleware
try:
    from asgi_headers import SecurityHeadersMiddleware
    application = SecurityHeadersMiddleware(application, {
        'X-Frame-Options': 'DENY',
        'X-Content-Type-Options': 'nosniff',
        'X-XSS-Protection': '1; mode=block',
    })
except ImportError:
    # Security headers middleware not installed
    pass

