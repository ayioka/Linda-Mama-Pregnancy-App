# pregnancy/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    ROLE_CHOICES = [
        ('mother', 'Mother'),
        ('clinician', 'Clinician'),
        ('admin', 'Administrator'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='mother')
    phone = models.CharField(max_length=15, blank=True)
    emergency_contact = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"{self.username} ({self.role})"

class PregnancyRecord(models.Model):
    TRIMESTER_CHOICES = [
        ('first', 'First Trimester'),
        ('second', 'Second Trimester'),
        ('third', 'Third Trimester'),
    ]
    
    mother = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'role': 'mother'})
    pregnancy_start_date = models.DateField()
    due_date = models.DateField()
    current_trimester = models.CharField(max_length=20, choices=TRIMESTER_CHOICES, default='first')
    status = models.CharField(max_length=20, default='active')
    
    def update_progress(self):
        weeks_pregnant = (timezone.now().date() - self.pregnancy_start_date).days // 7
        if weeks_pregnant < 13:
            self.current_trimester = 'first'
        elif weeks_pregnant < 27:
            self.current_trimester = 'second'
        else:
            self.current_trimester = 'third'
        self.save()
    
    def __str__(self):
        return f"Pregnancy record for {self.mother.username}"

class VitalsLog(models.Model):
    mother = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'mother'})
    date_recorded = models.DateTimeField(auto_now_add=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    blood_pressure_systolic = models.IntegerField(null=True, blank=True)
    blood_pressure_diastolic = models.IntegerField(null=True, blank=True)
    symptoms = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-date_recorded']

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    mother = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mother_appointments', limit_choices_to={'role': 'mother'})
    clinician = models.ForeignKey(User, on_delete=models.CASCADE, related_name='clinician_appointments', limit_choices_to={'role': 'clinician'})
    date_time = models.DateTimeField()
    location = models.CharField(max_length=200)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    
    def send_reminder(self):
        # Implementation for SMS/email reminders
        pass
    
    def __str__(self):
        return f"Appointment for {self.mother.username} with {self.clinician.username}"

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    timestamp = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Message from {self.sender.username} to {self.receiver.username}"

class EducationalContent(models.Model):
    CONTENT_TYPES = [
        ('article', 'Article'),
        ('video', 'Video'),
        ('tip', 'Tip'),
    ]
    
    TRIMESTER_TARGET = [
        ('all', 'All Trimesters'),
        ('first', 'First Trimester'),
        ('second', 'Second Trimester'),
        ('third', 'Third Trimester'),
    ]
    
    title = models.CharField(max_length=200)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    trimester_target = models.CharField(max_length=20, choices=TRIMESTER_TARGET, default='all')
    content = models.TextField()
    image = models.ImageField(upload_to='education_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title
