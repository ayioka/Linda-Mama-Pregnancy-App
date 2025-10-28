from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class Pregnancy(models.Model):
    TRIMESTER_CHOICES = (
        (1, 'First Trimester (1-12 weeks)'),
        (2, 'Second Trimester (13-26 weeks)'),
        (3, 'Third Trimester (27-40 weeks)'),
    )
    
    mother = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        limit_choices_to={'user_type': 'mother'}
    )
    start_date = models.DateField()
    due_date = models.DateField(null=True, blank=True)
    current_trimester = models.IntegerField(choices=TRIMESTER_CHOICES, default=1)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Pregnancies"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Pregnancy of {self.mother.get_full_name()} - {self.get_current_trimester_display()}"
    
    def save(self, *args, **kwargs):
        # Auto-calculate due date if not provided (40 weeks from start)
        if not self.due_date and self.start_date:
            self.due_date = self.start_date + timedelta(weeks=40)
        
        # Calculate current trimester based on weeks
        if self.start_date:
            today = timezone.now().date()
            weeks_pregnant = (today - self.start_date).days // 7
            if weeks_pregnant < 13:
                self.current_trimester = 1
            elif weeks_pregnant < 27:
                self.current_trimester = 2
            else:
                self.current_trimester = 3
        
        super().save(*args, **kwargs)
    
    def get_weeks_pregnant(self):
        """Calculate current weeks pregnant"""
        if self.start_date:
            today = timezone.now().date()
            weeks = (today - self.start_date).days // 7
            days = (today - self.start_date).days % 7
            return weeks, days
        return 0, 0
    
    def get_days_to_go(self):
        """Calculate days until due date"""
        if self.due_date:
            today = timezone.now().date()
            days = (self.due_date - today).days
            return max(0, days)
        return 0
    
    def get_progress_percentage(self):
        """Calculate pregnancy progress percentage"""
        if self.start_date and self.due_date:
            total_days = (self.due_date - self.start_date).days
            days_passed = (timezone.now().date() - self.start_date).days
            return min(100, max(0, int((days_passed / total_days) * 100)))
        return 0
    
    def get_baby_development_info(self):
        """Get baby development information based on weeks"""
        weeks, days = self.get_weeks_pregnant()
        development_info = {
            'size': 'Size information',
            'weight': 'Weight information', 
            'milestones': 'Development milestones'
        }
        # Add actual development data here
        return development_info

class HealthMetric(models.Model):
    pregnancy = models.ForeignKey(Pregnancy, on_delete=models.CASCADE, related_name='health_metrics')
    date_recorded = models.DateTimeField(default=timezone.now)
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Weight in kg")
    blood_pressure_systolic = models.IntegerField(null=True, blank=True, help_text="Systolic BP")
    blood_pressure_diastolic = models.IntegerField(null=True, blank=True, help_text="Diastolic BP")
    heart_rate = models.IntegerField(null=True, blank=True, help_text="Heart rate (BPM)")
    temperature = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, help_text="Temperature in °C")
    symptoms = models.TextField(blank=True, help_text="Any symptoms or concerns")
    notes = models.TextField(blank=True, help_text="Additional notes")
    
    class Meta:
        ordering = ['-date_recorded']
    
    def __str__(self):
        return f"Health metrics for {self.pregnancy.mother.get_full_name()} on {self.date_recorded.date()}"
    
    def get_blood_pressure(self):
        if self.blood_pressure_systolic and self.blood_pressure_diastolic:
            return f"{self.blood_pressure_systolic}/{self.blood_pressure_diastolic}"
        return "Not recorded"
