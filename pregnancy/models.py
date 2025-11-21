from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from django.db.models.signals import post_save
from django.dispatch import receiver
import re

# -------------------------------
# Custom User
# -------------------------------

class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(
        default=False,
        help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.'
    )

    class Meta:
        db_table = 'pregnancy_user'

    def clean(self):
        super().clean()
        if self.email:
            self.email = self.email.lower()

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def get_full_name(self):
        full_name = f'{self.first_name} {self.last_name}'.strip()
        return full_name if full_name else self.username

    def __str__(self):
        return self.username

# -------------------------------
# User Profile
# -------------------------------

class UserProfileManager(models.Manager):
    def patients(self):
        return self.filter(role=UserProfile.Roles.PATIENT)
    
    def clinicians(self):
        return self.filter(role=UserProfile.Roles.CLINICIAN)
    
    def pregnant_patients(self):
        return self.patients().exclude(due_date__isnull=True)
    
    def by_trimester(self, trimester):
        """Get patients in specific trimester"""
        today = date.today()
        if trimester == 1:
            # Weeks 1-13
            start_date = today - timedelta(days=13*7)
            end_date = today - timedelta(days=1*7)
        elif trimester == 2:
            # Weeks 14-26
            start_date = today - timedelta(days=26*7)
            end_date = today - timedelta(days=14*7)
        else:
            # Weeks 27-42
            start_date = today - timedelta(days=42*7)
            end_date = today - timedelta(days=27*7)
        
        return self.pregnant_patients().filter(
            due_date__range=[start_date, end_date]
        )

class UserProfile(models.Model):
    class Roles(models.TextChoices):
        PATIENT = 'patient', 'Patient'
        CLINICIAN = 'clinician', 'Healthcare Provider'
        ADMIN = 'admin', 'Administrator'

    BLOOD_TYPES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
        ('UNKNOWN', 'Unknown'),
    ]

    PREGNANCY_TYPES = [
        ('singleton', 'Singleton'),
        ('twins', 'Twins'),
        ('triplets', 'Triplets'),
        ('multiple', 'Multiple'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    role = models.CharField(max_length=10, choices=Roles.choices, default=Roles.PATIENT)
    phone_number = models.CharField(max_length=20, blank=True, help_text='Format: +254 XXX XXX XXX')
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=100, blank=True)
    blood_type = models.CharField(max_length=10, choices=BLOOD_TYPES, blank=True, default='UNKNOWN')
    allergies = models.TextField(blank=True)
    due_date = models.DateField(null=True, blank=True)
    last_menstrual_period = models.DateField(null=True, blank=True)
    height = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    pre_pregnancy_weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    pregnancy_type = models.CharField(max_length=10, choices=PREGNANCY_TYPES, default='singleton')
    gravida = models.PositiveIntegerField(default=1, help_text='Number of pregnancies')
    para = models.PositiveIntegerField(default=0, help_text='Number of live births')
    has_high_risk = models.BooleanField(default=False)
    primary_care_physician = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserProfileManager()

    class Meta:
        db_table = 'user_profile'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['role', 'due_date']),
            models.Index(fields=['due_date']),
            models.Index(fields=['created_at']),
        ]

    def clean(self):
        super().clean()
        
        # Enhanced due date validation
        if self.due_date:
            if self.due_date <= date.today():
                raise ValidationError({'due_date': 'Due date must be in the future.'})
            if self.due_date > date.today() + timedelta(days=320):  # ~46 weeks
                raise ValidationError({'due_date': 'Due date seems too far in the future.'})
        
        # Enhanced date of birth validation
        if self.date_of_birth:
            if self.date_of_birth >= date.today():
                raise ValidationError({'date_of_birth': 'Date of birth must be in the past.'})
            # Minimum age validation (e.g., 12 years)
            min_age_date = date.today() - timedelta(days=12*365)
            if self.date_of_birth > min_age_date:
                raise ValidationError({'date_of_birth': 'User must be at least 12 years old.'})
        
        # Phone number validation with regex
        if self.phone_number and not re.match(r'^\+?[\d\s\-\(\)]{10,}$', self.phone_number):
            raise ValidationError({'phone_number': 'Enter a valid phone number.'})

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def calculate_age(self):
        if not self.date_of_birth:
            return None
        today = date.today()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))

    def calculate_pregnancy_week(self):
        """Calculate current pregnancy week with enhanced accuracy"""
        if not self.due_date and not self.last_menstrual_period:
            return None
        
        today = date.today()
        
        # Use LMP if available, otherwise calculate from due date
        if self.last_menstrual_period:
            lmp_date = self.last_menstrual_period
        else:
            lmp_date = self.due_date - timedelta(days=280)
        
        if lmp_date > today:
            return None
        
        days_pregnant = (today - lmp_date).days
        if days_pregnant < 0:
            return None
        
        week = (days_pregnant // 7) + 1
        day = days_pregnant % 7
        
        return {
            'week': min(week, 42), 
            'day': day, 
            'total_days': days_pregnant,
            'weeks_completed': week - 1,
            'days_in_current_week': day,
            'estimated_due_date': lmp_date + timedelta(days=280)
        }

    def get_trimester(self):
        data = self.calculate_pregnancy_week()
        if not data:
            return None
        week = data['week']
        if week <= 13:
            return {'number': 1, 'name': 'First Trimester', 'message': 'Early development stage'}
        elif week <= 26:
            return {'number': 2, 'name': 'Second Trimester', 'message': 'Golden trimester - feeling better!'}
        else:
            return {'number': 3, 'name': 'Third Trimester', 'message': 'Final stretch - almost there!'}

    def get_pregnancy_progress(self):
        data = self.calculate_pregnancy_week()
        if not data:
            return 0
        return min(100, (data['week']/40)*100)

    def get_current_milestone(self):
        """Get the current pregnancy milestone"""
        week_data = self.calculate_pregnancy_week()
        if not week_data:
            return None
        
        try:
            return PregnancyMilestone.objects.get(week=week_data['week'])
        except PregnancyMilestone.DoesNotExist:
            return None

    def get_upcoming_appointments(self, limit=5):
        """Get upcoming appointments"""
        from django.utils import timezone
        return self.user.appointments.filter(
            date_time__gte=timezone.now()
        ).exclude(
            is_completed=True
        ).order_by('date_time')[:limit]

    @property
    def full_name(self):
        return self.user.get_full_name()

    @property
    def email(self):
        return self.user.email

    def __str__(self):
        return f"{self.user.username}'s Profile ({self.role})"

    def is_clinician(self):
        return self.role == self.Roles.CLINICIAN

    def is_admin(self):
        return self.role == self.Roles.ADMIN

    def is_patient(self):
        return self.role == self.Roles.PATIENT

# -------------------------------
# Pregnancy Milestones
# -------------------------------

class PregnancyMilestone(models.Model):
    week = models.PositiveIntegerField(help_text='Pregnancy week (1-42)', unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    baby_size = models.CharField(max_length=100)
    baby_weight = models.CharField(max_length=50)
    baby_length = models.CharField(max_length=50)
    key_developments = models.TextField()
    maternal_changes = models.TextField()
    health_tips = models.TextField()

    class Meta:
        db_table = 'pregnancy_milestone'
        ordering = ['week']

    def get_key_developments_list(self):
        return [dev.strip() for dev in self.key_developments.split('\n') if dev.strip()]

    def get_health_tips_list(self):
        return [tip.strip() for tip in self.health_tips.split('\n') if tip.strip()]

    def __str__(self):
        return f"Week {self.week}: {self.title}"

# -------------------------------
# Appointments
# -------------------------------

class Appointment(models.Model):
    class AppointmentType(models.TextChoices):
        PRENATAL = 'prenatal', 'Prenatal Checkup'
        ULTRASOUND = 'ultrasound', 'Ultrasound'
        LAB_TEST = 'lab_test', 'Lab Test'
        CONSULTATION = 'consultation', 'Consultation'
        OTHER = 'other', 'Other'

    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    appointment_type = models.CharField(max_length=20, choices=AppointmentType.choices, default=AppointmentType.PRENATAL)
    date_time = models.DateTimeField()
    location = models.CharField(max_length=200)
    healthcare_provider = models.CharField(max_length=100)
    notes = models.TextField(blank=True)
    is_completed = models.BooleanField(default=False)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='scheduled')
    duration = models.PositiveIntegerField(default=30, help_text='Duration in minutes')
    reminder_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'appointment'
        ordering = ['-date_time']
        indexes = [
            models.Index(fields=['user', 'date_time']),
            models.Index(fields=['date_time', 'is_completed']),
        ]

    def is_upcoming(self):
        from django.utils import timezone
        return self.date_time > timezone.now() and self.status in ['scheduled', 'confirmed']

    def get_time_until_appointment(self):
        from django.utils import timezone
        return self.date_time - timezone.now()

    def __str__(self):
        return f"{self.user.username} - {self.get_appointment_type_display()} - {self.date_time}"

# -------------------------------
# Health Metrics
# -------------------------------

class HealthMetric(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='health_metrics')
    date = models.DateField(default=date.today)
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    blood_pressure_systolic = models.PositiveIntegerField(null=True, blank=True)
    blood_pressure_diastolic = models.PositiveIntegerField(null=True, blank=True)
    fetal_heart_rate = models.PositiveIntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'health_metric'
        ordering = ['-date']
        unique_together = ['user', 'date']

    def __str__(self):
        return f"{self.user.username} - {self.date}"

# -------------------------------
# Signals
# -------------------------------

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()
