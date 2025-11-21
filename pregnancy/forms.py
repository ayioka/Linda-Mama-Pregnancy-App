from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date, datetime
from .models import UserProfile

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
            # Create user profile
            UserProfile.objects.create(user=user)
        
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
    
    class Meta:
        model = UserProfile
        fields = [
            'first_name', 'last_name', 'email',  # User model fields
            'phone_number', 'date_of_birth', 'address', 
            'emergency_contact', 'blood_type', 'allergies',
            'due_date', 'height', 'pre_pregnancy_weight'
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
            'blood_type': forms.Select(attrs={
                'class': 'form-control'
            }),
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
        return dob
    
    def clean_due_date(self):
        due_date = self.cleaned_data.get('due_date')
        if due_date and due_date <= date.today():
            raise ValidationError('Due date must be in the future.')
        return due_date
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number:
            # Basic phone number validation
            cleaned_phone = ''.join(filter(str.isdigit, phone_number))
            if len(cleaned_phone) < 10:
                raise ValidationError('Please enter a valid phone number.')
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
        from .models import HealthMetric
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
                'placeholder': 'Systolic (upper number)'
            }),
            'blood_pressure_diastolic': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Diastolic (lower number)'
            }),
            'fetal_heart_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Fetal heart rate in BPM'
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
            raise ValidationError('Please enter a valid systolic blood pressure reading.')
        return systolic
    
    def clean_blood_pressure_diastolic(self):
        diastolic = self.cleaned_data.get('blood_pressure_diastolic')
        if diastolic and (diastolic < 30 or diastolic > 150):
            raise ValidationError('Please enter a valid diastolic blood pressure reading.')
        return diastolic
    
    def clean_fetal_heart_rate(self):
        heart_rate = self.cleaned_data.get('fetal_heart_rate')
        if heart_rate and (heart_rate < 60 or heart_rate > 200):
            raise ValidationError('Please enter a valid fetal heart rate (typically 120-160 BPM).')
        return heart_rate


class AppointmentForm(forms.ModelForm):
    class Meta:
        from .models import Appointment
        model = Appointment
        fields = ['appointment_type', 'date_time', 'location', 'healthcare_provider', 'notes']
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
        return date_time
