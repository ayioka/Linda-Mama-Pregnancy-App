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
            import pregnancy.signals  # noqa: F401
            logger.info("Pregnancy app signals imported successfully")
        except ImportError as e:
            logger.warning(f"Could not import pregnancy signals: {e}")
        
        # Import checks (if they exist)
        try:
            from . import checks  # noqa: F401
            logger.info("Pregnancy app checks imported successfully")
        except ImportError as e:
            logger.debug(f"Pregnancy checks module not found: {e}")
        
        # Initialize default data after app is fully loaded
        self.initialize_default_data()
    
    def initialize_default_data(self):
        """
        Create default pregnancy milestones and initial data if they don't exist.
        This runs only when the app is fully ready.
        """
        try:
            # Import here to avoid circular imports
            from django.db import connection
            from django.core.management.color import no_style
            from django.db.backends.base.base import BaseDatabaseWrapper
            
            # Check if the table exists by trying to access it
            try:
                from .models import PregnancyMilestone
                
                # Simple check to see if we can query the table
                if hasattr(PregnancyMilestone, '_meta') and PregnancyMilestone._meta.db_table:
                    if not PregnancyMilestone.objects.exists():
                        self.create_default_milestones()
                        logger.info("Default pregnancy milestones created")
                
            except Exception as e:
                logger.debug(f"PregnancyMilestone table might not exist yet: {e}")
                
        except Exception as e:
            logger.debug(f"Error checking for default data initialization: {e}")
    
    def create_default_milestones(self):
        """
        Create default pregnancy milestones for key weeks.
        """
        try:
            from .models import PregnancyMilestone
            
            # Only create if they don't exist
            if PregnancyMilestone.objects.exists():
                return
                
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
                PregnancyMilestone.objects.get_or_create(
                    week=milestone_data['week'],
                    defaults=milestone_data
                )
                
            logger.info("Default pregnancy milestones created successfully")
            
        except Exception as e:
            logger.error(f"Error creating default milestones: {e}")
