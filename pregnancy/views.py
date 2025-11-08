from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm
from .models import UserProfile

def home(request):
    return render(request, 'pregnancy/home.html')

def custom_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'pregnancy/login.html', {'form': form})

def signup(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Create user profile
            UserProfile.objects.create(user=user)
            
            # Send welcome email
            try:
                send_mail(
                    'Welcome to Linda Mama Pregnancy Tracker!',
                    f'''Hello {user.first_name} {user.last_name},

Thank you for creating an account with Linda Mama Pregnancy Tracker!

Your account has been successfully created. You can now:
- Track your pregnancy week by week
- Access educational resources
- Connect with healthcare providers
- Monitor your health metrics

Start your journey by visiting your dashboard: http://127.0.0.1:8000/dashboard/

Best regards,
Linda Mama Team''',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
                messages.success(request, 'Account created successfully! Welcome email sent.')
            except Exception as e:
                messages.warning(request, 'Account created, but failed to send welcome email.')
            
            # Log the user in
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'pregnancy/signup.html', {'form': form})

@login_required
def dashboard(request):
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    context = {
        'profile': profile,
    }
    return render(request, 'pregnancy/dashboard.html', context)

@login_required
def profile(request):
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)
    
    context = {
        'form': form,
        'profile': profile,
    }
    return render(request, 'pregnancy/profile.html', context)

@login_required
def resources(request):
    return render(request, 'pregnancy/resources.html')

@login_required
def week_tracker(request):
    return render(request, 'pregnancy/week_tracker.html')

@login_required
def health_metrics(request):
    return render(request, 'pregnancy/health_metrics.html')

@login_required
def appointments(request):
    return render(request, 'pregnancy/appointments.html')

@login_required
def emergency(request):
    return render(request, 'pregnancy/emergency.html')

@login_required
def nutrition(request):
    return render(request, 'pregnancy/nutrition.html')

@login_required
def exercise(request):
    return render(request, 'pregnancy/exercise.html')

@login_required
def mental_health(request):
    return render(request, 'pregnancy/mental_health.html')

@login_required
def baby_development(request):
    return render(request, 'pregnancy/baby_development.html')
