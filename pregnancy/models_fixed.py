# pregnancy/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta
import uuid

class User(AbstractUser):
    ROLE_CHOICES = [
        ('mother', 'Expectant Mother'),
        ('clinician', 'Healthcare Provider'),
        ('admin', 'System Administrator'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='mother')        
    phone_number = models.CharField(max_length=15, blank=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f\"{self.get_full_name() or self.username} ({self.get_role_display()})\"     

    class Meta:
        ordering = ['-created_at']

class PregnancyProfile(models.Model):
    TRIMESTER_CHOICES = [
        ('first', 'First Trimester (1-12 weeks)'),
        ('second', 'Second Trimester (13-26 weeks)'),
        ('third', 'Third Trimester (27-40 weeks)'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # FIXED: Use string reference instead of direct User model
    mother = models.OneToOneField('pregnancy.User', on_delete=models.CASCADE, limit_choices_to={'role': 'mother'})
    last_menstrual_period = models.DateField()
    estimated_due_date = models.DateField()
    current_trimester = models.CharField(max_length=20, choices=TRIMESTER_CHOICES, default='first')
    blood_type = models.CharField(max_length=5, blank=True)
    known_allergies = models.TextField(blank=True)
    pre_existing_conditions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Calculate due date if not provided (40 weeks from LMP)
        if not self.estimated_due_date and self.last_menstrual_period:
            self.estimated_due_date = self.last_menstrual_period + timedelta(weeks=40)    

        # Update current trimester based on weeks pregnant
        if self.last_menstrual_period:
            weeks_pregnant = self.get_weeks_pregnant()
            if weeks_pregnant < 13:
                self.current_trimester = 'first'
            elif weeks_pregnant < 27:
                self.current_trimester = 'second'
            else:
                self.current_trimester = 'third'

        super().save(*args, **kwargs)

    def get_weeks_pregnant(self):
        if self.last_menstrual_period:
            days_pregnant = (timezone.now().date() - self.last_menstrual_period).days
            return days_pregnant // 7
        return 0

    def get_days_until_due(self):
        if self.estimated_due_date:
            days_until = (self.estimated_due_date - timezone.now().date()).days
            return max(0, days_until)
        return None

    def __str__(self):
        return f\"Pregnancy Profile - {self.mother.get_full_name()}\"
