from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    USER_TYPES = (
        ('mother', 'Expectant Mother'),
        ('clinician', 'Healthcare Provider'),
        ('admin', 'System Administrator'),
    )
    
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='mother')
    phone_number = models.CharField(max_length=15, blank=True)
    emergency_contact = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True)
    bio = models.TextField(blank=True)
    date_modified = models.DateTimeField(auto_now=True)
    
    # Clinician-specific fields
    license_number = models.CharField(max_length=50, blank=True)
    specialization = models.CharField(max_length=100, blank=True)
    hospital_affiliation = models.CharField(max_length=200, blank=True)
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_user_type_display()})"
    
    def get_initials(self):
        """Get user initials for avatar"""
        if self.first_name and self.last_name:
            return f"{self.first_name[0]}{self.last_name[0]}".upper()
        return self.username[0:2].upper()
    
    class Meta:
        ordering = ['-date_joined']
