from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date, timedelta
from django.db.models.signals import post_save
from django.dispatch import receiver


class User(AbstractUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=False)
    last_name = models.CharField(max_length=30, blank=False)
    is_active = models.BooleanField(
        default=False,
        help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.'
    )

    class Meta:
        db_table = 'pregnancy_user'  # <-- custom table name

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
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-'),
        ('UNKNOWN', 'Unknown'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    role = models.CharField(max_length=10, choices=Roles.choices, default=Roles.PATIENT)
    phone_number = models.CharField(max_length=20, blank=True, help_text='Format: +255 XXX XXX XXX')
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=100, blank=True)
    blood_type = models.CharField(max_length=10, choices=BLOOD_TYPES, blank=True, default='UNKNOWN')
    allergies = models.TextField(blank=True)
    due_date = models.DateField(null=True, blank=True)
    height = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    pre_pregnancy_weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_profile'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
        ordering = ['-created_at']

    def clean(self):
        super().clean()
        if self.due_date and self.due_date <= date.today():
            raise ValidationError({'due_date': 'Due date must be in the future.'})
        if self.date_of_birth and self.date_of_birth >= date.today():
            raise ValidationError({'date_of_birth': 'Date of birth must be in the past.'})
        if self.phone_number and not self.phone_number.replace('+', '').replace(' ', '').isdigit():
            raise ValidationError({'phone_number': 'Phone number should contain only numbers, spaces, and + sign.'})

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def calculate_age(self):
        if not self.date_of_birth:
            return None
        today = date.today()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))

    def calculate_pregnancy_week(self):
        if not self.due_date:
            return None
        today = date.today()
        lmp_date = self.due_date - timedelta(days=280)
        if lmp_date > today:
            return None
        days_pregnant = (today - lmp_date).days
        week = (days_pregnant // 7) + 1
        day = days_pregnant % 7
        return {'week': min(week, 42), 'day': day, 'total_days': days_pregnant, 'weeks_completed': week - 1, 'days_in_current_week': day}

    def get_trimester(self):
        pregnancy_data = self.calculate_pregnancy_week()
        if not pregnancy_data:
            return None
        week = pregnancy_data['week']
        if week <= 13:
            return {'number': 1, 'name': 'First Trimester', 'message': 'Early development stage'}
        elif week <= 26:
            return {'number': 2, 'name': 'Second Trimester', 'message': 'Golden trimester - feeling better!'}
        else:
            return {'number': 3, 'name': 'Third Trimester', 'message': 'Final stretch - almost there!'}

    def get_pregnancy_progress(self):
        pregnancy_data = self.calculate_pregnancy_week()
        if not pregnancy_data:
            return 0
        week = pregnancy_data['week']
        return min(100, (week / 40) * 100)

    def is_clinician(self):
        return self.role == self.Roles.CLINICIAN

    def is_admin(self):
        return self.role == self.Roles.ADMIN

    def is_patient(self):
        return self.role == self.Roles.PATIENT

    @property
    def full_name(self):
        return self.user.get_full_name()

    @property
    def email(self):
        return self.user.email

    def __str__(self):
        return f"{self.user.username}'s Profile ({self.role})"


# Signals to auto-create UserProfile
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()
