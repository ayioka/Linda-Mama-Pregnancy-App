from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date, datetime, timedelta
from .models import UserProfile, Appointment, HealthMetric, PregnancyMilestone

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True, 
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address',
            'autocomplete': 'email'
        }),
        help_text='Required. Enter a valid email address.'
    )
    first_name = forms.CharField(
        max_length=30, 
        required=True, 
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your first name',
            'autocomplete': 'given-name'
        })
    )
    last_name = forms.CharField(
        max_length=30, 
        required=True, 
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your last name',
            'autocomplete': 'family-name'
        })
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Choose a username',
            'autocomplete': 'username'
        }),
        help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Update all fields with form-control class
        for field_name, field in self.fields.items():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'
            
            # Add aria labels for accessibility
            if field_name == 'username':
                field.widget.attrs['aria-describedby'] = 'usernameHelp'
            elif field_name == 'email':
                field.widget.attrs['aria-describedby'] = 'emailHelp'
        
        # Customize password help text
        self.fields['password1'].widget.attrs.update({
            'placeholder': 'Create a strong password',
            'autocomplete': 'new-password'
        })
        self.fields['password2'].widget.attrs.update({
            'placeholder': 'Confirm your password',
            'autocomplete': 'new-password'
        })
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower()
            if User.objects.filter(email=email).exists():
                raise ValidationError('A user with this email already exists.')
        return email
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            if User.objects.filter(username=username).exists():
                raise ValidationError('A user with this username already exists.')
        return username
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.is_active = False  # Require email activation
        
        if commit:
            user.save()
            # Create user profile only if it doesn't exist
            UserProfile.objects.get_or_create(user=user)
        
        return user


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your username or email',
            'autocomplete': 'username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password',
            'autocomplete': 'current-password'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure all fields have form-control class
        for field_name, field in self.fields.items():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            # Allow login with email or username
            return username.lower()
        return username


class UserProfileForm(forms.ModelForm):
    # Additional fields from User model
    first_name = forms.CharField(
        max_length=30, 
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name'
        })
    )
    last_name = forms.CharField(
        max_length=30, 
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address'
        })
    )
    due_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        help_text='Expected due date (EDD)'
    )
    last_menstrual_period = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        help_text='First day of your last menstrual period'
    )
    
    class Meta:
        model = UserProfile
        fields = [
            'first_name', 'last_name', 'email',  # User model fields
            'phone_number', 'date_of_birth', 'address', 
            'emergency_contact', 'blood_type', 'allergies',
            'due_date', 'last_menstrual_period', 'height', 'pre_pregnancy_weight',
            'pregnancy_type', 'gravida', 'para', 'has_high_risk', 'primary_care_physician'
        ]
        widgets = {
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+255 XXX XXX XXX'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'form-control'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3,
                'placeholder': 'Enter your complete address'
            }),
            'emergency_contact': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Name and phone number'
            }),
            'blood_type': forms.Select(attrs={'class': 'form-control'}),
            'allergies': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3,
                'placeholder': 'List any allergies or medical conditions'
            }),
            'height': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Height in cm',
                'step': '0.1',
                'min': '100',
                'max': '250'
            }),
            'pre_pregnancy_weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Weight before pregnancy in kg',
                'step': '0.1',
                'min': '30',
                'max': '200'
            }),
            'pregnancy_type': forms.Select(attrs={'class': 'form-control'}),
            'gravida': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '20'
            }),
            'para': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '20'
            }),
            'has_high_risk': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'primary_care_physician': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Doctor\'s name'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Initialize User model fields with current values
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
        
        # Add form-control class to all fields
        for field_name, field in self.fields.items():
            if 'class' not in field.widget.attrs:
                if field_name != 'has_high_risk':
                    field.widget.attrs['class'] = 'form-control'
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and self.user:
            email = email.lower()
            # Check if email is already used by another user
            if User.objects.filter(email=email).exclude(pk=self.user.pk).exists():
                raise ValidationError('This email is already registered with another account.')
        return email
    
    def clean_date_of_birth(self):
        dob = self.cleaned_data.get('date_of_birth')
        if dob and dob >= date.today():
            raise ValidationError('Date of birth must be in the past.')
        
        # Validate minimum age (12 years)
        if dob:
            min_age_date = date.today() - timedelta(days=12*365)
            if dob > min_age_date:
                raise ValidationError('You must be at least 12 years old to use this service.')
        return dob
    
    def clean_due_date(self):
        due_date = self.cleaned_data.get('due_date')
        if due_date:
            if due_date <= date.today():
                raise ValidationError('Due date must be in the future.')
            if due_date > date.today() + timedelta(days=320):
                raise ValidationError('Due date seems too far in the future. Please verify.')
        return due_date
    
    def clean_last_menstrual_period(self):
        lmp = self.cleaned_data.get('last_menstrual_period')
        if lmp and lmp >= date.today():
            raise ValidationError('Last menstrual period date must be in the past.')
        return lmp
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number:
            # Basic phone number validation
            import re
            if not re.match(r'^\+?[\d\s\-\(\)]{10,}$', phone_number):
                raise ValidationError('Please enter a valid phone number format.')
        return phone_number
    
    def clean_height(self):
        height = self.cleaned_data.get('height')
        if height and (height < 100 or height > 250):
            raise ValidationError('Please enter a valid height between 100cm and 250cm.')
        return height
    
    def clean_pre_pregnancy_weight(self):
        weight = self.cleaned_data.get('pre_pregnancy_weight')
        if weight and (weight < 30 or weight > 200):
            raise ValidationError('Please enter a valid weight between 30kg and 200kg.')
        return weight
    
    def clean_gravida(self):
        gravida = self.cleaned_data.get('gravida')
        if gravida and (gravida < 1 or gravida > 20):
            raise ValidationError('Please enter a valid number of pregnancies (1-20).')
        return gravida
    
    def clean_para(self):
        para = self.cleaned_data.get('para')
        gravida = self.cleaned_data.get('gravida')
        if para and para > gravida:
            raise ValidationError('Number of live births cannot exceed total pregnancies.')
        return para
    
    def save(self, commit=True):
        profile = super().save(commit=False)
        
        # Update User model fields
        if self.user:
            self.user.first_name = self.cleaned_data['first_name']
            self.user.last_name = self.cleaned_data['last_name']
            self.user.email = self.cleaned_data['email']
            if commit:
                self.user.save()
        
        if commit:
            profile.save()
        
        return profile


class HealthMetricForm(forms.ModelForm):
    class Meta:
        model = HealthMetric
        fields = ['date', 'weight', 'blood_pressure_systolic', 'blood_pressure_diastolic', 'fetal_heart_rate', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'placeholder': 'Current weight in kg'
            }),
            'blood_pressure_systolic': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Systolic (upper number)',
                'min': '50',
                'max': '250'
            }),
            'blood_pressure_diastolic': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Diastolic (lower number)',
                'min': '30',
                'max': '150'
            }),
            'fetal_heart_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Fetal heart rate in BPM',
                'min': '60',
                'max': '200'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Any additional notes...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if 'class' not in self.fields[field].widget.attrs:
                self.fields[field].widget.attrs['class'] = 'form-control'
    
    def clean_blood_pressure_systolic(self):
        systolic = self.cleaned_data.get('blood_pressure_systolic')
        if systolic and (systolic < 50 or systolic > 250):
            raise ValidationError('Please enter a valid systolic blood pressure reading (50-250).')
        return systolic
    
    def clean_blood_pressure_diastolic(self):
        diastolic = self.cleaned_data.get('blood_pressure_diastolic')
        if diastolic and (diastolic < 30 or diastolic > 150):
            raise ValidationError('Please enter a valid diastolic blood pressure reading (30-150).')
        return diastolic
    
    def clean_fetal_heart_rate(self):
        heart_rate = self.cleaned_data.get('fetal_heart_rate')
        if heart_rate and (heart_rate < 60 or heart_rate > 200):
            raise ValidationError('Please enter a valid fetal heart rate (60-200 BPM).')
        return heart_rate
    
    def clean_weight(self):
        weight = self.cleaned_data.get('weight')
        if weight and (weight < 30 or weight > 200):
            raise ValidationError('Please enter a valid weight (30-200 kg).')
        return weight


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['appointment_type', 'date_time', 'location', 'healthcare_provider', 'notes', 'duration']
        widgets = {
            'appointment_type': forms.Select(attrs={'class': 'form-control'}),
            'date_time': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Hospital or clinic name'
            }),
            'healthcare_provider': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Doctor or healthcare provider name'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Any special instructions or notes...'
            }),
            'duration': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Duration in minutes',
                'min': '15',
                'max': '240'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if 'class' not in self.fields[field].widget.attrs:
                self.fields[field].widget.attrs['class'] = 'form-control'
    
    def clean_date_time(self):
        date_time = self.cleaned_data.get('date_time')
        if date_time and date_time <= timezone.now():
            raise ValidationError('Appointment must be scheduled for a future date and time.')
        
        # Validate appointment is not too far in the future (1 year max)
        if date_time and date_time > timezone.now() + timedelta(days=365):
            raise ValidationError('Appointment cannot be scheduled more than 1 year in advance.')
        
        return date_time
    
    def clean_duration(self):
        duration = self.cleaned_data.get('duration')
        if duration and (duration < 15 or duration > 240):
            raise ValidationError('Appointment duration must be between 15 and 240 minutes.')
        return duration


class PregnancyMilestoneForm(forms.ModelForm):
    class Meta:
        model = PregnancyMilestone
        fields = ['week', 'title', 'description', 'baby_size', 'baby_weight', 'baby_length', 
                 'key_developments', 'maternal_changes', 'health_tips']
        widgets = {
            'week': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '42'
            }),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'baby_size': forms.TextInput(attrs={'class': 'form-control'}),
            'baby_weight': forms.TextInput(attrs={'class': 'form-control'}),
            'baby_length': forms.TextInput(attrs={'class': 'form-control'}),
            'key_developments': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'maternal_changes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'health_tips': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if 'class' not in self.fields[field].widget.attrs:
                self.fields[field].widget.attrs['class'] = 'form-control'
    
    def clean_week(self):
        week = self.cleaned_data.get('week')
        if week and (week < 1 or week > 42):
            raise ValidationError('Pregnancy week must be between 1 and 42.')
        return week


class ClinicianPatientSearchForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by name, email, or phone...'
        })
    )
    trimester = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'All Trimesters'),
            ('1', 'First Trimester'),
            ('2', 'Second Trimester'),
            ('3', 'Third Trimester'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    high_risk = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )


class AppointmentStatusForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['status', 'is_completed', 'notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'is_completed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
