from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)

class PregnancyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pregnancy'
    verbose_name = 'Pregnancy Management'
    
    def ready(self):
        """
        Import signals and perform any other initialization when the app is ready.
        This method is called once Django starts.
        """
        # Import signals to ensure they are registered
        try:
            import pregnancy.signals  # noqa: F401
            logger.info("Pregnancy app signals imported successfully")
        except ImportError as e:
            logger.warning(f"Could not import pregnancy signals: {e}")
        
        # Import and register custom system checks
        try:
            from . import checks  # noqa: F401
            logger.info("Pregnancy app checks imported successfully")
        except ImportError as e:
            logger.debug(f"Pregnancy checks module not found: {e}")
        
        # Initialize default pregnancy milestones if they don't exist
        self.initialize_default_data()
        
        # Register custom admin site if needed
        self.setup_admin()
    
    def initialize_default_data(self):
        """
        Create default pregnancy milestones and initial data if they don't exist.
        This runs only once when the app starts.
        """
        try:
            from .models import PregnancyMilestone
            
            # Only run if we're in a ready state and the table exists
            if not hasattr(self, '_default_data_initialized'):
                # Check if we have any milestones, if not create default ones
                if not PregnancyMilestone.objects.exists():
                    self.create_default_milestones()
                    logger.info("Default pregnancy milestones created")
                
                self._default_data_initialized = True
                
        except Exception as e:
            logger.error(f"Error initializing default data: {e}")
    
    def create_default_milestones(self):
        """
        Create default pregnancy milestones for weeks 4-40.
        This provides basic development information for each pregnancy week.
        """
        from .models import PregnancyMilestone
        
        default_milestones = [
            {
                'week': 4,
                'title': 'Neural Tube Formation',
                'description': 'The neural tube, which becomes the brain and spinal cord, is forming.',
                'baby_size': 'poppy seed',
                'baby_weight': '0.5g',
                'baby_length': '0.1cm',
                'key_developments': 'Neural tube forms\nHeart begins to beat\nBasic circulatory system develops',
                'maternal_changes': 'You might not feel any changes yet, but amazing development is happening!',
                'health_tips': 'Start taking prenatal vitamins with folic acid\nAvoid alcohol and smoking\nSchedule your first prenatal appointment'
            },
            {
                'week': 8,
                'title': 'Major Organs Begin Forming',
                'description': 'All major organs and body systems are starting to develop.',
                'baby_size': 'kidney bean',
                'baby_weight': '1g',
                'baby_length': '1.6cm',
                'key_developments': 'All major organs begin to form\nFingers and toes start developing\nEyes and ears forming',
                'maternal_changes': 'You may experience morning sickness, fatigue, and breast tenderness.',
                'health_tips': 'Eat small, frequent meals to manage nausea\nGet plenty of rest\nStay hydrated with water and ginger tea'
            },
            {
                'week': 12,
                'title': 'Reflex Development',
                'description': 'Your baby is developing reflexes and can make movements.',
                'baby_size': 'lime',
                'baby_weight': '14g',
                'baby_length': '5.4cm',
                'key_developments': 'Reflexes develop\nSex organs differentiate\nVocal cords form',
                'maternal_changes': 'Morning sickness may start to improve. Your uterus is growing above the pelvic bone.',
                'health_tips': 'Consider sharing your pregnancy news\nWear comfortable, loose-fitting clothes\nContinue prenatal vitamins'
            },
            {
                'week': 20,
                'title': 'Hearing Development',
                'description': 'Your baby can now hear sounds and is developing regular sleep cycles.',
                'baby_size': 'banana',
                'baby_weight': '300g',
                'baby_length': '16.4cm',
                'key_developments': 'Baby can hear sounds\nRegular sleep-wake cycles begin\nVernix caseosa forms on skin',
                'maternal_changes': 'You may start feeling baby movements - gentle flutters called quickening!',
                'health_tips': 'Talk and sing to your baby\nEat iron-rich foods\nConsider an anatomy ultrasound scan'
            },
            {
                'week': 28,
                'title': 'Eyes Opening',
                'description': 'Your baby can open and close eyes and is developing brain rapidly.',
                'baby_size': 'eggplant',
                'baby_weight': '1kg',
                'baby_length': '37.6cm',
                'key_developments': 'Eyes can open and close\nBrain develops rapidly\nLungs continue maturing',
                'maternal_changes': 'You may feel more pronounced movements. Backache and heartburn are common.',
                'health_tips': 'Monitor baby movements\nPractice relaxation techniques\nStart prenatal classes'
            },
            {
                'week': 36,
                'title': 'Positioning for Birth',
                'description': 'Your baby is getting into position for birth and lungs are nearly mature.',
                'baby_size': 'head of romaine lettuce',
                'baby_weight': '2.6kg',
                'baby_length': '47.4cm',
                'key_developments': 'Lungs nearly mature\nHead may engage in pelvis\nMost lanugo hair disappears',
                'maternal_changes': 'Baby may drop lower, making breathing easier but walking uncomfortable.',
                'health_tips': 'Pack your hospital bag\nRest when possible\nPractice breathing exercises'
            },
            {
                'week': 40,
                'title': 'Full Term Development',
                'description': 'Your baby is fully developed and ready for birth!',
                'baby_size': 'small pumpkin',
                'baby_weight': '3.4kg',
                'baby_length': '51.2cm',
                'key_developments': 'Full-term development\nReady for birth\nOrgans fully functional',
                'maternal_changes': 'Your body is preparing for labor. You may experience Braxton Hicks contractions.',
                'health_tips': 'Watch for signs of labor\nStay hydrated and rested\nHave emergency contacts ready'
            }
        ]
        
        for milestone_data in default_milestones:
            PregnancyMilestone.objects.create(**milestone_data)
    
    def setup_admin(self):
        """
        Customize admin site for the pregnancy app.
        """
        try:
            from django.contrib import admin
            from django.contrib.admin.sites import site as default_site
            
            # Custom admin registration can be done here
            # This is where you might register custom admin classes
            
            logger.info("Pregnancy app admin setup completed")
            
        except Exception as e:
            logger.error(f"Error setting up admin: {e}")


# Optional: Custom system checks for the pregnancy app
def check_app_settings(app_configs, **kwargs):
    """
    Custom system check for pregnancy app configuration.
    """
    from django.conf import settings
    from django.core.checks import Warning, register
    
    errors = []
    
    # Check if email settings are configured for activation emails
    if not hasattr(settings, 'DEFAULT_FROM_EMAIL') or not settings.DEFAULT_FROM_EMAIL:
        errors.append(
            Warning(
                'DEFAULT_FROM_EMAIL not set',
                hint='Set DEFAULT_FROM_EMAIL in settings for activation emails to work properly',
                obj='pregnancy',
                id='pregnancy.W001',
            )
        )
    
    # Check if site framework is installed (needed for activation emails)
    if 'django.contrib.sites' not in settings.INSTALLED_APPS:
        errors.append(
            Warning(
                'django.contrib.sites not in INSTALLED_APPS',
                hint='Add django.contrib.sites to INSTALLED_APPS for proper email activation links',
                obj='pregnancy',
                id='pregnancy.W002',
            )
        )
    
    return errors


# Register the custom check
try:
    from django.core.checks import register
    register(check_app_settings)
except ImportError:
    # Django not fully initialized yet, which is fine
    pass
