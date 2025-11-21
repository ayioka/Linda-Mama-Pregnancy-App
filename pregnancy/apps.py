from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)

class PregnancyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pregnancy'
    verbose_name = 'Pregnancy Management'
    
    def ready(self):
        """
        Import signals when the app is ready.
        This method is called once Django starts.
        """
        # Import signals to ensure they are registered
        try:
            # Import signals module but don't trigger model imports
            from . import signals
            logger.info("Pregnancy app signals imported successfully")
        except ImportError as e:
            logger.warning(f"Could not import pregnancy signals: {e}")
