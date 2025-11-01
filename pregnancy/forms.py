from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import User, PregnancyProfile, VitalsRecord, Appointment, Message, EmergencyAlert, EducationalContent
from datetime import date, timedelta

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    phone_number = forms.CharField(max_length=15, required=True)
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, initial='mother')
    
    # Additional fields for mothers
    last_menstrual_period = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        help_text="First day of your last menstrual period"
    )
    blood_type = forms.CharField(max_length=5, required=False)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name', 
            'phone_number', 'role', 'password1', 'password2',
            'last_menstrual_period', 'blood_type'
        ]
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with this email already exists.")
        return email
    
    def clean_last_menstrual_period(self):
        lmp = self.cleaned_data.get('last_menstrual_period')
        if lmp and lmp > date.today():
            raise ValidationError("Last menstrual period cannot be in the future.")
        return lmp

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'profile_picture']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True

class PregnancyProfileForm(forms.ModelForm):
    class Meta:
        model = PregnancyProfile
        fields = [
            'last_menstrual_period', 'blood_type', 
            'known_allergies', 'pre_existing_conditions'
        ]
        widgets = {
            'last_menstrual_period': forms.DateInput(attrs={'type': 'date'}),
            'known_allergies': forms.Textarea(attrs={'rows': 3}),
            'pre_existing_conditions': forms.Textarea(attrs={'rows': 3}),
        }
    
    def clean_last_menstrual_period(self):
        lmp = self.cleaned_data.get('last_menstrual_period')
        if lmp and lmp > date.today():
            raise ValidationError("Last menstrual period cannot be in the future.")
        return lmp

class VitalsRecordForm(forms.ModelForm):
    class Meta:
        model = VitalsRecord
        fields = [
            'weight_kg', 'blood_pressure_systolic', 'blood_pressure_diastolic',
            'temperature', 'fetal_heart_rate', 'symptoms', 'notes'
        ]
        widgets = {
            'symptoms': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Describe any symptoms you are experiencing...'}),
            'notes': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Additional notes...'}),
        }
    
    def clean_blood_pressure_systolic(self):
        systolic = self.cleaned_data.get('blood_pressure_systolic')
        if systolic and (systolic < 50 or systolic > 250):
            raise ValidationError("Systolic blood pressure must be between 50 and 250.")
        return systolic
    
    def clean_blood_pressure_diastolic(self):
        diastolic = self.cleaned_data.get('blood_pressure_diastolic')
        if diastolic and (diastolic < 30 or diastolic > 150):
            raise ValidationError("Diastolic blood pressure must be between 30 and 150.")
        return diastolic
    
    def clean_weight_kg(self):
        weight = self.cleaned_data.get('weight_kg')
        if weight and (weight < 30 or weight > 200):
            raise ValidationError("Weight must be between 30 and 200 kg.")
        return weight
    
    def clean_temperature(self):
        temp = self.cleaned_data.get('temperature')
        if temp and (temp < 35 or temp > 42):
            raise ValidationError("Temperature must be between 35°C and 42°C.")
        return temp
    
    def clean_fetal_heart_rate(self):
        heart_rate = self.cleaned_data.get('fetal_heart_rate')
        if heart_rate and (heart_rate < 60 or heart_rate > 200):
            raise ValidationError("Fetal heart rate must be between 60 and 200 BPM.")
        return heart_rate

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = [
            'clinician', 'appointment_type', 'scheduled_date', 
            'duration_minutes', 'location', 'reason'
        ]
        widgets = {
            'scheduled_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'reason': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show clinicians in the dropdown
        self.fields['clinician'].queryset = User.objects.filter(role='clinician', is_active=True)
    
    def clean_scheduled_date(self):
        scheduled_date = self.cleaned_data.get('scheduled_date')
        if scheduled_date and scheduled_date < timezone.now():
            raise ValidationError("Appointment cannot be scheduled in the past.")
        return scheduled_date

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['receiver', 'subject', 'content', 'is_urgent']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # Don't allow sending messages to yourself
            self.fields['receiver'].queryset = User.objects.exclude(id=user.id).filter(is_active=True)

class EmergencyAlertForm(forms.ModelForm):
    class Meta:
        model = EmergencyAlert
        fields = ['urgency_level', 'symptoms', 'location']
        widgets = {
            'symptoms': forms.Textarea(attrs={
                'rows': 4, 
                'placeholder': 'Describe your symptoms in detail...'
            }),
            'location': forms.TextInput(attrs={
                'placeholder': 'Your current location or address'
            }),
        }

class EducationalContentForm(forms.ModelForm):
    class Meta:
        model = EducationalContent
        fields = [
            'title', 'slug', 'content_type', 'trimester_target', 
            'summary', 'content', 'featured_image', 'video_url',
            'read_time_minutes', 'is_featured', 'is_active'
        ]
        widgets = {
            'summary': forms.Textarea(attrs={'rows': 3}),
            'content': forms.Textarea(attrs={'rows': 10}),
        }
    
    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        if slug and EducationalContent.objects.filter(slug=slug).exists():
            if self.instance and self.instance.slug == slug:
                return slug
            raise ValidationError("A content item with this slug already exists.")
        return slug

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    subject = forms.CharField(max_length=200, required=True)
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 5}), required=True)
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if len(name.strip()) < 2:
            raise ValidationError("Please enter a valid name.")
        return name.strip()
