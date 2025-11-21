# pregnancy/context_processors.py

from django.conf import settings

def app_settings(request):
    """
    Makes global settings available in all templates
    """
    return {
        'APP_NAME': 'Linda Mama Pregnancy Tracker',
        'DEBUG': settings.DEBUG,
        'PREGNANCY_TRACKER_CONFIG': settings.PREGNANCY_TRACKER_CONFIG,
    }
