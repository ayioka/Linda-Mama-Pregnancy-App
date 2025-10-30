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
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"
    
    class Meta:
        ordering = ['-created_at']

class PregnancyProfile(models.Model):
    TRIMESTER_CHOICES = [
        ('first', 'First Trimester (1-12 weeks)'),
        ('second', 'Second Trimester (13-26 weeks)'),
        ('third', 'Third Trimester (27-40 weeks)'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mother = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'role': 'mother'})
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
            weeks_pregnant = (timezone.now().date() - self.last_menstrual_period).days // 7
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
        return f"Pregnancy Profile - {self.mother.get_full_name()}"

class VitalsRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mother = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'mother'})
    record_date = models.DateTimeField(default=timezone.now)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    blood_pressure_systolic = models.IntegerField(null=True, blank=True)
    blood_pressure_diastolic = models.IntegerField(null=True, blank=True)
    temperature = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    fetal_heart_rate = models.IntegerField(null=True, blank=True)
    symptoms = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-record_date']
        verbose_name = 'Vitals Record'
        verbose_name_plural = 'Vitals Records'
    
    def __str__(self):
        return f"Vitals - {self.mother.username} - {self.record_date.strftime('%Y-%m-%d')}"

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]
    
    TYPE_CHOICES = [
        ('antenatal', 'Antenatal Checkup'),
        ('ultrasound', 'Ultrasound Scan'),
        ('blood_test', 'Blood Test'),
        ('consultation', 'Doctor Consultation'),
        ('emergency', 'Emergency Visit'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mother = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mother_appointments', limit_choices_to={'role': 'mother'})
    clinician = models.ForeignKey(User, on_delete=models.CASCADE, related_name='clinician_appointments', limit_choices_to={'role': 'clinician'})
    appointment_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='antenatal')
    scheduled_date = models.DateTimeField()
    duration_minutes = models.IntegerField(default=30)
    location = models.CharField(max_length=200)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    notes = models.TextField(blank=True)
    reminder_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['scheduled_date']
    
    def __str__(self):
        return f"{self.get_appointment_type_display()} - {self.mother.username} - {self.scheduled_date.strftime('%Y-%m-%d %H:%M')}"

class EducationalContent(models.Model):
    CONTENT_TYPE_CHOICES = [
        ('article', 'Article'),
        ('video', 'Video'),
        ('infographic', 'Infographic'),
        ('tip', 'Daily Tip'),
        ('guide', 'Guide'),
    ]
    
    TRIMESTER_TARGET = [
        ('all', 'All Trimesters'),
        ('first', 'First Trimester'),
        ('second', 'Second Trimester'),
        ('third', 'Third Trimester'),
        ('postpartum', 'Postpartum'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES)
    trimester_target = models.CharField(max_length=20, choices=TRIMESTER_TARGET, default='all')
    summary = models.TextField()
    content = models.TextField()
    featured_image = models.ImageField(upload_to='content_images/', blank=True, null=True)
    video_url = models.URLField(blank=True)
    read_time_minutes = models.IntegerField(default=5)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Educational Content'
        verbose_name_plural = 'Educational Content'
    
    def __str__(self):
        return self.title

class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    subject = models.CharField(max_length=200)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    is_urgent = models.BooleanField(default=False)
    parent_message = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Message: {self.subject} - {self.sender.username} to {self.receiver.username}"

class EmergencyAlert(models.Model):
    URGENCY_LEVELS = [
        ('low', 'Low Urgency'),
        ('medium', 'Medium Urgency'),
        ('high', 'High Urgency'),
        ('critical', 'Critical Emergency'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mother = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'mother'})
    urgency_level = models.CharField(max_length=20, choices=URGENCY_LEVELS, default='medium')
    symptoms = models.TextField()
    location = models.CharField(max_length=200)
    is_responded = models.BooleanField(default=False)
    responded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='responded_alerts')
    response_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Emergency Alert - {self.mother.username} - {self.get_urgency_level_display()}"
