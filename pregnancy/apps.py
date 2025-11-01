from django.apps import AppConfig


class PregnancyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pregnancy'
    verbose_name = 'Pregnancy Management'
    
    def ready(self):
        import pregnancy.signals
