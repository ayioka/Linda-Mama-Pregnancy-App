from django import forms
from .models import Pregnancy, HealthMetric
from django.utils import timezone

class PregnancyForm(forms.ModelForm):
    class Meta:
        model = Pregnancy
        fields = ['start_date', 'due_date', 'notes']
        widgets = {
            'start_date': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'form-control',
                'max': timezone.now().date().isoformat()
            }),
            'due_date': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'form-control'
            }),
            'notes': forms.Textarea(attrs={
                'rows': 4, 
                'class': 'form-control',
                'placeholder': 'Any initial notes about your pregnancy...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field != 'notes':
                self.fields[field].widget.attrs.update({'class': 'form-control'})

class HealthMetricForm(forms.ModelForm):
    class Meta:
        model = HealthMetric
        fields = [
            'weight', 'blood_pressure_systolic', 'blood_pressure_diastolic',
            'heart_rate', 'temperature', 'symptoms', 'notes'
        ]
        widgets = {
            'symptoms': forms.Textarea(attrs={
                'rows': 3, 
                'class': 'form-control',
                'placeholder': 'Describe any symptoms you\'re experiencing...'
            }),
            'notes': forms.Textarea(attrs={
                'rows': 3, 
                'class': 'form-control',
                'placeholder': 'Additional notes...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
            self.fields[field].required = False
