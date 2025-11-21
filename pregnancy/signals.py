from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a UserProfile when a new User is created"""
    if created:
        # Import inside function to avoid circular imports
        from .models import UserProfile
        try:
            UserProfile.objects.create(user=instance)
        except Exception:
            # Table might not exist during migrations
            pass

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save UserProfile when User is saved"""
    # Import inside function to avoid circular imports
    from .models import UserProfile
    try:
        if hasattr(instance, 'userprofile'):
            instance.userprofile.save()
    except UserProfile.DoesNotExist:
        # Profile doesn't exist yet
        pass
    except Exception:
        # Table might not exist during migrations
        pass
