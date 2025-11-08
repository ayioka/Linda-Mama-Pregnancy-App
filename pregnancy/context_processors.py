# pregnancy/context_processors.py

def global_settings(request):
    """
    Makes global settings available in all templates
    """
    from django.conf import settings
    
    return {
        'APP_NAME': 'Linda Mama Pregnancy Tracker',
        'DEBUG': settings.DEBUG,
        'PREGNANCY_TRACKER_CONFIG': settings.PREGNANCY_TRACKER_CONFIG,
    }
