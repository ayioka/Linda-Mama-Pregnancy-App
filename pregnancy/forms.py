# pregnancy/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import User, PregnancyProfile, VitalsRecord, Appointment, Message, EmergencyAlert, EducationalContent
from datetime import date, timedelta

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'})
    )
    first_name = forms.CharField(
        max_length=30, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your first name'})
    )
    last_name = forms.CharField(
        max_length=30, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your last name'})
    )
    phone_number = forms.CharField(
        max_length=15, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your phone number'})
    )
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES, 
        initial='mother',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # Additional fields for mothers
    last_menstrual_period = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        help_text="First day of your last menstrual period"
    )
    blood_type = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'Select blood type'),
            ('A+', 'A+'), ('A-', 'A-'),
            ('B+', 'B+'), ('B-', 'B-'),
            ('AB+', 'AB+'), ('AB-', 'AB-'),
            ('O+', 'O+'), ('O-', 'O-')
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name', 
            'phone_number', 'role', 'password1', 'password2',
            'last_menstrual_period', 'blood_type'
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Choose a username'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to password fields
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm password'})
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with this email already exists.")
        return email
    
    def clean_last_menstrual_period(self):
        lmp = self.cleaned_data.get('last_menstrual_period')
        if lmp:
            if lmp > date.today():
                raise ValidationError("Last menstrual period cannot be in the future.")
            # Check if LMP is not too far in the past (more than 1 year)
            if (date.today() - lmp).days > 365:
                raise ValidationError("Last menstrual period seems too far in the past. Please consult a healthcare provider.")
        return lmp
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone_number = self.cleaned_data['phone_number']
        
        if commit:
            user.save()
            
            # Create pregnancy profile for mothers
            if user.role == 'mother' and self.cleaned_data.get('last_menstrual_period'):
                pregnancy_profile = PregnancyProfile(
                    mother=user,
                    last_menstrual_period=self.cleaned_data['last_menstrual_period'],
                    blood_type=self.cleaned_data.get('blood_type', '')
                )
                pregnancy_profile.save()
        
        return user

class UserProfileForm(forms.ModelForm):
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    profile_picture = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'phone_number', 
            'date_of_birth', 'profile_picture',
            'emergency_contact_name', 'emergency_contact_phone'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_name': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True
    
    def clean_date_of_birth(self):
        dob = self.cleaned_data.get('date_of_birth')
        if dob and dob > date.today():
            raise ValidationError("Date of birth cannot be in the future.")
        return dob
    
    def clean_emergency_contact_phone(self):
        phone = self.cleaned_data.get('emergency_contact_phone')
        if phone and not phone.replace(' ', '').replace('-', '').replace('+', '').isdigit():
            raise ValidationError("Please enter a valid phone number.")
        return phone

class PregnancyProfileForm(forms.ModelForm):
    class Meta:
        model = PregnancyProfile
        fields = [
            'last_menstrual_period', 'blood_type', 
            'known_allergies', 'pre_existing_conditions'
        ]
        widgets = {
            'last_menstrual_period': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'blood_type': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('', 'Select blood type'),
                ('A+', 'A+'), ('A-', 'A-'),
                ('B+', 'B+'), ('B-', 'B-'),
                ('AB+', 'AB+'), ('AB-', 'AB-'),
                ('O+', 'O+'), ('O-', 'O-')
            ]),
            'known_allergies': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'List any known allergies...'}),
            'pre_existing_conditions': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'List any pre-existing medical conditions...'}),
        }
    
    def clean_last_menstrual_period(self):
        lmp = self.cleaned_data.get('last_menstrual_period')
        if lmp:
            if lmp > date.today():
                raise ValidationError("Last menstrual period cannot be in the future.")
            if (date.today() - lmp).days > 365:
                raise ValidationError("Last menstrual period seems too far in the past. Please consult a healthcare provider.")
        return lmp

class VitalsRecordForm(forms.ModelForm):
    record_date = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        initial=timezone.now
    )
    
    class Meta:
        model = VitalsRecord
        fields = [
            'record_date', 'weight_kg', 'blood_pressure_systolic', 'blood_pressure_diastolic',
            'temperature', 'fetal_heart_rate', 'symptoms', 'notes'
        ]
        widgets = {
            'weight_kg': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'Weight in kg'}),
            'blood_pressure_systolic': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Systolic'}),
            'blood_pressure_diastolic': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Diastolic'}),
            'temperature': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'Temperature in °C'}),
            'fetal_heart_rate': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Fetal heart rate in BPM'}),
            'symptoms': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Describe any symptoms you are experiencing...'}),
            'notes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'placeholder': 'Additional notes...'}),
        }
    
    def clean_blood_pressure_systolic(self):
        systolic = self.cleaned_data.get('blood_pressure_systolic')
        if systolic:
            if systolic < 50 or systolic > 250:
                raise ValidationError("Systolic blood pressure must be between 50 and 250 mmHg.")
        return systolic
    
    def clean_blood_pressure_diastolic(self):
        diastolic = self.cleaned_data.get('blood_pressure_diastolic')
        if diastolic:
            if diastolic < 30 or diastolic > 150:
                raise ValidationError("Diastolic blood pressure must be between 30 and 150 mmHg.")
        return diastolic
    
    def clean_weight_kg(self):
        weight = self.cleaned_data.get('weight_kg')
        if weight:
            if weight < 30 or weight > 200:
                raise ValidationError("Weight must be between 30 and 200 kg.")
        return weight
    
    def clean_temperature(self):
        temp = self.cleaned_data.get('temperature')
        if temp:
            if temp < 35 or temp > 42:
                raise ValidationError("Temperature must be between 35°C and 42°C.")
        return temp
    
    def clean_fetal_heart_rate(self):
        heart_rate = self.cleaned_data.get('fetal_heart_rate')
        if heart_rate:
            if heart_rate < 60 or heart_rate > 200:
                raise ValidationError("Fetal heart rate must be between 60 and 200 BPM.")
        return heart_rate
    
    def clean(self):
        cleaned_data = super().clean()
        systolic = cleaned_data.get('blood_pressure_systolic')
        diastolic = cleaned_data.get('blood_pressure_diastolic')
        
        if systolic and diastolic:
            if systolic <= diastolic:
                raise ValidationError("Systolic blood pressure must be higher than diastolic blood pressure.")
        
        return cleaned_data

class AppointmentForm(forms.ModelForm):
    scheduled_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'})
    )
    
    class Meta:
        model = Appointment
        fields = [
            'clinician', 'appointment_type', 'scheduled_date', 
            'duration_minutes', 'location', 'reason', 'notes'
        ]
        widgets = {
            'clinician': forms.Select(attrs={'class': 'form-control'}),
            'appointment_type': forms.Select(attrs={'class': 'form-control'}),
            'duration_minutes': forms.Select(attrs={'class': 'form-control'}, choices=[
                (15, '15 minutes'),
                (30, '30 minutes'),
                (45, '45 minutes'),
                (60, '60 minutes'),
                (90, '90 minutes'),
            ]),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Appointment location'}),
            'reason': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Reason for appointment...'}),
            'notes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'placeholder': 'Additional notes...'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # Only show active clinicians in the dropdown
        self.fields['clinician'].queryset = User.objects.filter(role='clinician', is_active=True)
        
        # Set initial duration
        if not self.instance.pk:
            self.fields['duration_minutes'].initial = 30
    
    def clean_scheduled_date(self):
        scheduled_date = self.cleaned_data.get('scheduled_date')
        if scheduled_date:
            if scheduled_date < timezone.now():
                raise ValidationError("Appointment cannot be scheduled in the past.")
            
            # Check if appointment is within reasonable future (1 year)
            max_future_date = timezone.now() + timedelta(days=365)
            if scheduled_date > max_future_date:
                raise ValidationError("Appointment cannot be scheduled more than 1 year in advance.")
        
        return scheduled_date
    
    def clean_duration_minutes(self):
        duration = self.cleaned_data.get('duration_minutes')
        if duration and (duration < 15 or duration > 180):
            raise ValidationError("Appointment duration must be between 15 and 180 minutes.")
        return duration

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['receiver', 'subject', 'content', 'is_urgent']
        widgets = {
            'receiver': forms.Select(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Message subject'}),
            'content': forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'Type your message here...'}),
            'is_urgent': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # Don't allow sending messages to yourself
            self.fields['receiver'].queryset = User.objects.exclude(id=user.id).filter(is_active=True)
            
            # For mothers, show clinicians; for clinicians, show mothers
            if user.role == 'mother':
                self.fields['receiver'].queryset = self.fields['receiver'].queryset.filter(role='clinician')
            elif user.role == 'clinician':
                self.fields['receiver'].queryset = self.fields['receiver'].queryset.filter(role='mother')

class EmergencyAlertForm(forms.ModelForm):
    class Meta:
        model = EmergencyAlert
        fields = ['urgency_level', 'symptoms', 'location']
        widgets = {
            'urgency_level': forms.Select(attrs={'class': 'form-control'}),
            'symptoms': forms.Textarea(attrs={
                'rows': 4, 
                'class': 'form-control',
                'placeholder': 'Describe your symptoms in detail. Include when they started, severity, and any other relevant information...'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your current location or address'
            }),
        }
    
    def clean_symptoms(self):
        symptoms = self.cleaned_data.get('symptoms')
        if not symptoms or len(symptoms.strip()) < 10:
            raise ValidationError("Please provide a detailed description of your symptoms (at least 10 characters).")
        return symptoms

class EducationalContentForm(forms.ModelForm):
    class Meta:
        model = EducationalContent
        fields = [
            'title', 'slug', 'content_type', 'trimester_target', 
            'summary', 'content', 'featured_image', 'video_url',
            'read_time_minutes', 'is_featured', 'is_active'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter content title'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'url-slug'}),
            'content_type': forms.Select(attrs={'class': 'form-control'}),
            'trimester_target': forms.Select(attrs={'class': 'form-control'}),
            'summary': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Brief summary of the content...'}),
            'content': forms.Textarea(attrs={'rows': 10, 'class': 'form-control', 'placeholder': 'Main content...'}),
            'featured_image': forms.FileInput(attrs={'class': 'form-control'}),
            'video_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com/video'}),
            'read_time_minutes': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        if slug:
            # Ensure slug is URL-friendly
            if not slug.replace('-', '').isalnum():
                raise ValidationError("Slug can only contain letters, numbers, and hyphens.")
            
            # Check for uniqueness
            qs = EducationalContent.objects.filter(slug=slug)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError("A content item with this slug already exists.")
        return slug
    
    def clean_read_time_minutes(self):
        read_time = self.cleaned_data.get('read_time_minutes')
        if read_time and (read_time < 1 or read_time > 120):
            raise ValidationError("Read time must be between 1 and 120 minutes.")
        return read_time

class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=100, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your name'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your email'})
    )
    subject = forms.CharField(
        max_length=200, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject'})
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5, 'class': 'form-control', 'placeholder': 'Your message...'}), 
        required=True
    )
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if len(name.strip()) < 2:
            raise ValidationError("Please enter a valid name.")
        return name.strip()

class AppointmentStatusForm(forms.ModelForm):
    """Form for updating appointment status (used by clinicians)"""
    class Meta:
        model = Appointment
        fields = ['status', 'notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Appointment notes...'}),
        }

class EmergencyAlertResponseForm(forms.ModelForm):
    """Form for responding to emergency alerts (used by clinicians)"""
    class Meta:
        model = EmergencyAlert
        fields = ['response_notes']
        widgets = {
            'response_notes': forms.Textarea(attrs={
                'rows': 4, 
                'class': 'form-control',
                'placeholder': 'Enter your response and recommendations...'
            }),
        }
    
    def clean_response_notes(self):
        notes = self.cleaned_data.get('response_notes')
        if not notes or len(notes.strip()) < 10:
            raise ValidationError("Please provide a detailed response (at least 10 characters).")
        return notes

class ContentSearchForm(forms.Form):
    """Form for searching educational content"""
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search articles, videos, tips...'
        })
    )
    content_type = forms.ChoiceField(
        required=False,
        choices=[('', 'All Types')] + EducationalContent.CONTENT_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    trimester_target = forms.ChoiceField(
        required=False,
        choices=[('', 'All Trimesters')] + EducationalContent.TRIMESTER_TARGET,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
