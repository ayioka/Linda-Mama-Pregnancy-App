# pregnancy/apps.py
from django.apps import AppConfig


class PregnancyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pregnancy'
    verbose_name = 'Pregnancy Management'
    
    def ready(self):
        """
        Import signals and perform any other initialization when the app is ready.
        This method is called once Django starts.
        """
        try:
            import pregnancy.signals  # noqa: F401
        except ImportError:
            # Signals module doesn't exist yet, which is fine during initial setup
            pass
