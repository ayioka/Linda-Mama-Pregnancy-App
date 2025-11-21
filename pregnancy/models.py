from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date, timedelta

class User(AbstractUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=False)
    last_name = models.CharField(max_length=30, blank=False)
    is_active = models.BooleanField(
        default=False,
        help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.'
    )
    
    # Remove the duplicate email field from AbstractUser
    class Meta:
        db_table = 'auth_user'
    
    def clean(self):
        """Validate user data"""
        super().clean()
        if self.email:
            self.email = self.email.lower()
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def get_full_name(self):
        """Return first_name + last_name with fallback to username"""
        full_name = f'{self.first_name} {self.last_name}'.strip()
        return full_name if full_name else self.username
    
    def __str__(self):
        return self.username


class UserProfile(models.Model):
    class Roles(models.TextChoices):
        PATIENT = 'patient', 'Patient'
        CLINICIAN = 'clinician', 'Healthcare Provider'
        ADMIN = 'admin', 'Administrator'
    
    BLOOD_TYPES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
        ('UNKNOWN', 'Unknown'),
    ]
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='userprofile'
    )
    role = models.CharField(
        max_length=10,
        choices=Roles.choices,
        default=Roles.PATIENT
    )
    phone_number = models.CharField(
        max_length=20, 
        blank=True,
        help_text='Format: +255 XXX XXX XXX'
    )
    date_of_birth = models.DateField(
        null=True, 
        blank=True,
        help_text='Your date of birth'
    )
    address = models.TextField(
        blank=True,
        help_text='Your complete address'
    )
    emergency_contact = models.CharField(
        max_length=100, 
        blank=True,
        help_text='Name and phone number of emergency contact'
    )
    blood_type = models.CharField(
        max_length=10, 
        choices=BLOOD_TYPES, 
        blank=True,
        default='UNKNOWN'
    )
    allergies = models.TextField(
        blank=True,
        help_text='List any allergies or medical conditions'
    )
    due_date = models.DateField(
        null=True, 
        blank=True,
        help_text='Expected due date (EDD)'
    )
    height = models.DecimalField(
        max_digits=4, 
        decimal_places=1,
        null=True, 
        blank=True,
        help_text='Height in centimeters'
    )
    pre_pregnancy_weight = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        null=True, 
        blank=True,
        help_text='Weight before pregnancy in kg'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profile'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
        ordering = ['-created_at']
    
    def clean(self):
        """Validate profile data"""
        super().clean()
        
        # Validate due date is in future
        if self.due_date and self.due_date <= date.today():
            raise ValidationError({
                'due_date': 'Due date must be in the future.'
            })
        
        # Validate date of birth is in past
        if self.date_of_birth and self.date_of_birth >= date.today():
            raise ValidationError({
                'date_of_birth': 'Date of birth must be in the past.'
            })
        
        # Validate phone number format (basic validation)
        if self.phone_number and not self.phone_number.replace('+', '').replace(' ', '').isdigit():
            raise ValidationError({
                'phone_number': 'Phone number should contain only numbers, spaces, and + sign.'
            })
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def calculate_age(self):
        """Calculate user's age from date of birth"""
        if not self.date_of_birth:
            return None
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
    
    def calculate_pregnancy_week(self):
        """Calculate current pregnancy week based on due date"""
        if not self.due_date:
            return None
        
        today = date.today()
        
        # Last Menstrual Period (LMP) = due_date - 280 days
        lmp_date = self.due_date - timedelta(days=280)
        
        # If LMP is in future, pregnancy hasn't started
        if lmp_date > today:
            return None
        
        days_pregnant = (today - lmp_date).days
        week = (days_pregnant // 7) + 1
        day = days_pregnant % 7
        
        return {
            'week': min(week, 42),  # Allow for up to 42 weeks
            'day': day,
            'total_days': days_pregnant,
            'weeks_completed': week - 1,
            'days_in_current_week': day
        }
    
    def get_trimester(self):
        """Get current trimester based on pregnancy week"""
        pregnancy_data = self.calculate_pregnancy_week()
        if not pregnancy_data:
            return None
        
        week = pregnancy_data['week']
        
        if week <= 13:
            return {
                'number': 1,
                'name': 'First Trimester',
                'message': 'Early development stage'
            }
        elif week <= 26:
            return {
                'number': 2,
                'name': 'Second Trimester',
                'message': 'Golden trimester - feeling better!'
            }
        else:
            return {
                'number': 3,
                'name': 'Third Trimester',
                'message': 'Final stretch - almost there!'
            }
    
    def get_pregnancy_progress(self):
        """Calculate pregnancy progress percentage"""
        pregnancy_data = self.calculate_pregnancy_week()
        if not pregnancy_data:
            return 0
        
        week = pregnancy_data['week']
        return min(100, (week / 40) * 100)
    
    def is_clinician(self):
        """Check if user is a healthcare provider"""
        return self.role == self.Roles.CLINICIAN
    
    def is_admin(self):
        """Check if user is an administrator"""
        return self.role == self.Roles.ADMIN
    
    def is_patient(self):
        """Check if user is a patient"""
        return self.role == self.Roles.PATIENT
    
    @property
    def full_name(self):
        """Get user's full name"""
        return self.user.get_full_name()
    
    @property
    def email(self):
        """Get user's email"""
        return self.user.email
    
    def __str__(self):
        return f"{self.user.username}'s Profile ({self.role})"


class PregnancyMilestone(models.Model):
    """Model to store pregnancy milestones and development information"""
    week = models.PositiveIntegerField(
        help_text='Pregnancy week (1-42)'
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    baby_size = models.CharField(
        max_length=100,
        help_text='Size comparison (e.g., "size of a blueberry")'
    )
    baby_weight = models.CharField(
        max_length=50,
        help_text='Approximate weight'
    )
    baby_length = models.CharField(
        max_length=50,
        help_text='Approximate length'
    )
    key_developments = models.TextField(
        help_text='Key developmental milestones (one per line)'
    )
    maternal_changes = models.TextField(
        help_text='Common maternal changes and symptoms'
    )
    health_tips = models.TextField(
        help_text='Health and wellness tips (one per line)'
    )
    
    class Meta:
        db_table = 'pregnancy_milestone'
        verbose_name = 'Pregnancy Milestone'
        verbose_name_plural = 'Pregnancy Milestones'
        ordering = ['week']
        unique_together = ['week']
    
    def get_key_developments_list(self):
        """Return key developments as list"""
        return [dev.strip() for dev in self.key_developments.split('\n') if dev.strip()]
    
    def get_health_tips_list(self):
        """Return health tips as list"""
        return [tip.strip() for tip in self.health_tips.split('\n') if tip.strip()]
    
    def __str__(self):
        return f"Week {self.week}: {self.title}"


class Appointment(models.Model):
    """Model for medical appointments"""
    class AppointmentType(models.TextChoices):
        PRENATAL = 'prenatal', 'Prenatal Checkup'
        ULTRASOUND = 'ultrasound', 'Ultrasound'
        LAB_TEST = 'lab_test', 'Lab Test'
        CONSULTATION = 'consultation', 'Consultation'
        OTHER = 'other', 'Other'
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='appointments'
    )
    appointment_type = models.CharField(
        max_length=20,
        choices=AppointmentType.choices,
        default=AppointmentType.PRENATAL
    )
    date_time = models.DateTimeField()
    location = models.CharField(max_length=200)
    healthcare_provider = models.CharField(
        max_length=100,
        help_text='Doctor or healthcare provider name'
    )
    notes = models.TextField(blank=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'appointment'
        ordering = ['-date_time']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_appointment_type_display()} - {self.date_time}"


class HealthMetric(models.Model):
    """Model for tracking health metrics during pregnancy"""
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='health_metrics'
    )
    date = models.DateField(default=date.today)
    weight = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        null=True, 
        blank=True,
        help_text='Current weight in kg'
    )
    blood_pressure_systolic = models.PositiveIntegerField(
        null=True, 
        blank=True,
        help_text='Systolic blood pressure'
    )
    blood_pressure_diastolic = models.PositiveIntegerField(
        null=True, 
        blank=True,
        help_text='Diastolic blood pressure'
    )
    fetal_heart_rate = models.PositiveIntegerField(
        null=True, 
        blank=True,
        help_text='Fetal heart rate (BPM)'
    )
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'health_metric'
        ordering = ['-date']
        unique_together = ['user', 'date']
    
    def __str__(self):
        return f"{self.user.username} - {self.date}"


# Signal to create user profile when user is created
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create user profile automatically when user is created"""
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save user profile when user is saved"""
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()
