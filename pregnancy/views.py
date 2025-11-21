from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging

from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm
from .models import UserProfile
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)

# Decorator to handle user profile retrieval
def get_user_profile(view_func):
    def wrapper(request, *args, **kwargs):
        try:
            profile = request.user.userprofile
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=request.user)
        return view_func(request, profile, *args, **kwargs)
    return wrapper

def home(request):
    return render(request, 'pregnancy/home.html')

def custom_login(request):
    if request.user.is_authenticated:
        return redirect_to_role_based_dashboard(request.user)
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            return redirect_to_role_based_dashboard(user)
        else:
            messages.error(request, 'Invalid username or password, or your account is not activated yet.')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'pregnancy/login.html', {'form': form})

def redirect_to_role_based_dashboard(user):
    """Redirect user based on their role"""
    try:
        profile = user.userprofile
        if profile.role == UserProfile.Roles.CLINICIAN:
            return redirect('clinician_dashboard')
        elif profile.role == UserProfile.Roles.ADMIN:
            return redirect('admin:index')
        else:
            return redirect('dashboard')
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=user)
        return redirect('dashboard')

def signup(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # user.is_active = False created in form.save()
            
            try:
                send_activation_email(request, user)
                messages.success(request, 'Account created! Please check your email to activate your account.')
                logger.info(f"Activation email sent to {user.email}")
            except Exception as e:
                logger.error(f"Failed to send activation email to {user.email}: {str(e)}")
                messages.warning(request, 'Account created but we could not send activation email. Please contact support.')
            
            return redirect('login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'pregnancy/register.html', {'form': form})

def send_activation_email(request, user):
    """Send account activation email"""
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    
    # Use current site for absolute URL
    from django.contrib.sites.shortcuts import get_current_site
    current_site = get_current_site(request)
    activation_link = f"http://{current_site.domain}/activate/{uid}/{token}/"
    
    subject = 'Activate your Linda Mama Pregnancy Tracker Account'
    message = render_to_string('pregnancy/email_activation.txt', {
        'user': user,
        'activation_link': activation_link,
        'site_name': current_site.name,
    })
    
    html_message = render_to_string('pregnancy/email_activation.html', {
        'user': user,
        'activation_link': activation_link,
        'site_name': current_site.name,
    })
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
        html_message=html_message
    )

def activate(request, uidb64, token):
    """Activate user account"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        if user.is_active:
            messages.info(request, 'Your account is already active.')
        else:
            user.is_active = True
            user.save()
            messages.success(request, 'Your account has been activated successfully!')
        
        # Ensure profile exists and log the user in
        profile, created = UserProfile.objects.get_or_create(user=user)
        if created:
            logger.info(f"Created user profile for {user.email}")
        
        login(request, user)
        
        # Send welcome email after activation
        try:
            send_welcome_email(request, user)
        except Exception as e:
            logger.warning(f"Failed to send welcome email to {user.email}: {str(e)}")
        
        return redirect_to_role_based_dashboard(user)
    else:
        messages.error(request, 'Activation link is invalid or has expired.')
        return redirect('home')

def send_welcome_email(request, user):
    """Send welcome email after account activation"""
    from django.contrib.sites.shortcuts import get_current_site
    current_site = get_current_site(request)
    dashboard_url = f"http://{current_site.domain}/dashboard/"
    
    subject = 'Welcome to Linda Mama Pregnancy Tracker!'
    message = render_to_string('pregnancy/welcome_email.txt', {
        'user': user,
        'dashboard_url': dashboard_url,
        'site_name': current_site.name,
    })
    
    html_message = render_to_string('pregnancy/welcome_email.html', {
        'user': user,
        'dashboard_url': dashboard_url,
        'site_name': current_site.name,
    })
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
        html_message=html_message
    )

def calculate_pregnancy_week(due_date, today=None):
    """
    Calculate pregnancy week based on last menstrual period (LMP)
    Standard medical calculation: LMP = due_date - 280 days (40 weeks)
    """
    if today is None:
        today = date.today()
    
    if not due_date or due_date < today:
        return None
    
    lmp_date = due_date - timedelta(days=280)
    days_pregnant = (today - lmp_date).days
    
    if days_pregnant < 0:
        return None
    
    week = (days_pregnant // 7) + 1
    day = days_pregnant % 7
    
    return {
        'week': min(week, 42),  # Allow for up to 42 weeks
        'day': day,
        'total_days': days_pregnant,
        'weeks_completed': week - 1,
        'days_in_current_week': day
    }

@login_required
@get_user_profile
def dashboard(request, profile):
    """User dashboard with pregnancy progress"""
    pregnancy_data = None
    current_trimester = "Not set"
    trimester_message = "Set your due date in your profile to track your pregnancy progress"
    
    if profile.due_date:
        pregnancy_data = calculate_pregnancy_week(profile.due_date)
        
        if pregnancy_data:
            current_week = pregnancy_data['week']
            
            # Calculate progress percentage (0-100%)
            progress_percentage = min(100, (current_week / 40) * 100)
            
            # Determine trimester
            if current_week <= 13:
                current_trimester = "First Trimester"
                trimester_message = "Early development stage - take care of yourself!"
            elif current_week <= 26:
                current_trimester = "Second Trimester"
                trimester_message = "Golden trimester - many women feel their best during this time!"
            else:
                current_trimester = "Third Trimester"
                trimester_message = "Final stretch - you're almost there!"
        else:
            progress_percentage = 0
            current_week = None
    else:
        progress_percentage = 0
        current_week = None
    
    context = {
        'profile': profile,
        'pregnancy_data': pregnancy_data,
        'current_week': current_week,
        'progress_percentage': progress_percentage,
        'current_trimester': current_trimester,
        'trimester_message': trimester_message,
    }
    return render(request, 'pregnancy/dashboard.html', context)

@login_required
@get_user_profile
def profile(request, profile):
    """User profile management"""
    if request.method == 'POST':
        # Update user fields
        user = request.user
        user.first_name = request.POST.get('first_name', '').strip() or user.first_name
        user.last_name = request.POST.get('last_name', '').strip() or user.last_name
        
        email = request.POST.get('email', '').strip()
        if email and email != user.email:
            user.email = email
            # You might want to verify email changes
        
        user.save()
        
        # Update profile fields with validation
        profile.phone_number = request.POST.get('phone_number', '').strip() or profile.phone_number
        
        # Validate date of birth
        dob_str = request.POST.get('date_of_birth', '').strip()
        if dob_str:
            try:
                dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
                if dob < date.today():
                    profile.date_of_birth = dob
                else:
                    messages.error(request, 'Date of birth must be in the past.')
            except ValueError:
                messages.error(request, 'Invalid date format for date of birth.')
        
        profile.blood_type = request.POST.get('blood_type', '').strip() or profile.blood_type
        profile.emergency_contact = request.POST.get('emergency_contact', '').strip() or profile.emergency_contact
        profile.allergies = request.POST.get('allergies', '').strip() or profile.allergies
        profile.address = request.POST.get('address', '').strip() or profile.address
        
        # Validate due date
        due_date_str = request.POST.get('due_date', '').strip()
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
                if due_date > date.today():
                    profile.due_date = due_date
                else:
                    messages.error(request, 'Due date must be in the future.')
            except ValueError:
                messages.error(request, 'Invalid date format for due date.')
        
        profile.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    
    context = {'profile': profile}
    return render(request, 'pregnancy/profile.html', context)

@login_required
@get_user_profile
def baby_development(request, profile):
    """Baby development information based on current week"""
    pregnancy_data = calculate_pregnancy_week(profile.due_date) if profile.due_date else None
    current_week = pregnancy_data['week'] if pregnancy_data else None
    
    development_data = get_development_data(current_week)
    
    context = {
        'profile': profile,
        'pregnancy_data': pregnancy_data,
        'current_week': current_week,
        **development_data
    }
    return render(request, 'pregnancy/baby_development.html', context)

def get_development_data(week):
    """Get comprehensive baby development information"""
    if not week or week < 1 or week > 42:
        return {
            'baby_size': 'Not available',
            'baby_weight': 'Not available',
            'baby_length': 'Not available',
            'key_developments': ['Set your due date to see development information'],
            'maternal_changes': 'Set your due date to see maternal changes',
            'health_tips': ['Set your due date to get personalized tips'],
            'upcoming_milestones': ['Set your due date to track milestones']
        }
    
    return {
        'baby_size': get_size_comparison(week),
        'baby_weight': calculate_baby_weight(week),
        'baby_length': calculate_baby_length(week),
        'key_developments': get_key_developments(week),
        'maternal_changes': get_maternal_changes(week),
        'health_tips': get_health_tips(week),
        'upcoming_milestones': get_upcoming_milestones(week),
    }

def get_size_comparison(week):
    """Get baby size comparison to common objects"""
    comparisons = {
        1-4: "Poppy seed to sesame seed", 5-8: "Apple seed to kidney bean",
        9-12: "Grape to lime", 13-16: "Lemon to avocado",
        17-20: "Turnip to banana", 21-24: "Carrot to corn",
        25-28: "Rutabaga to eggplant", 29-32: "Butternut squash to squash",
        33-36: "Pineapple to head of romaine", 37-40: "Swiss chard to pumpkin",
        41-42: "Small watermelon"
    }
    
    for range_key, comparison in comparisons.items():
        if isinstance(range_key, int) and week == range_key:
            return comparison
        elif isinstance(range_key, tuple) and range_key[0] <= week <= range_key[1]:
            return comparison
    
    return "Growing baby"

def calculate_baby_weight(week):
    """Calculate approximate baby weight based on week"""
    if week <= 8:
        return f"{week * 0.5:.1f}g"
    elif week <= 12:
        return f"{8 + (week - 8) * 2:.1f}g"
    elif week <= 20:
        return f"{((week - 12) * 25 + 14):.0f}g"
    elif week <= 28:
        return f"{((week - 20) * 100 + 300) / 1000:.1f}kg"
    else:
        return f"{((week - 28) * 200 + 1000) / 1000:.1f}kg"

def calculate_baby_length(week):
    """Calculate approximate baby length based on week"""
    if week <= 8:
        return f"{week * 0.2:.1f}cm"
    elif week <= 12:
        return f"{1.6 + (week - 8) * 1.0:.1f}cm"
    elif week <= 20:
        return f"{5.4 + (week - 12) * 1.5:.1f}cm"
    elif week <= 28:
        return f"{16.4 + (week - 20) * 3.0:.1f}cm"
    else:
        return f"{37.6 + (week - 28) * 1.8:.1f}cm"

def get_key_developments(week):
    """Get key developmental milestones"""
    milestones = {
        4: ["Neural tube forms", "Heart begins to beat"],
        8: ["All major organs begin to form", "Fingers and toes start developing"],
        12: ["Reflexes develop", "Sex organs differentiate"],
        16: ["Hearing develops", "Muscles strengthen"],
        20: ["Vernix caseosa forms", "Regular sleep cycles begin"],
        24: ["Taste buds form", "Lungs develop"],
        28: ["Eyes can open and close", "Brain develops rapidly"],
        32: ["Bones fully developed", "Lanugo hair begins to disappear"],
        36: ["Lungs nearly mature", "Head may engage in pelvis"],
        40: ["Full-term development", "Ready for birth!"]
    }
    
    closest_week = min(milestones.keys(), key=lambda x: abs(x - week))
    return milestones.get(closest_week, ["Baby is growing and developing beautifully!"])

def get_maternal_changes(week):
    """Get maternal changes and symptoms"""
    changes = {
        4: "You might experience fatigue, tender breasts, or morning sickness.",
        8: "Nausea and food aversions are common. Rest when you can.",
        12: "Many women start feeling better as the first trimester ends.",
        16: "You might feel baby's first movements - gentle flutters!",
        20: "Energy returns! This is often called the 'golden period'.",
        24: "Baby's movements become stronger and more regular.",
        28: "You may experience backache and need to urinate more frequently.",
        32: "Braxton Hicks contractions may begin. Stay hydrated!",
        36: "Baby drops lower - breathing becomes easier but walking may be uncomfortable.",
        40: "Your body is preparing for labor. Rest and stay hydrated."
    }
    
    closest_week = min(changes.keys(), key=lambda x: abs(x - week))
    return changes.get(closest_week, "Listen to your body and rest when needed.")

def get_health_tips(week):
    """Get personalized health tips"""
    tips = {
        1-13: [
            "Take prenatal vitamins with folic acid",
            "Avoid alcohol, smoking, and raw foods",
            "Get plenty of rest",
            "Eat small, frequent meals to manage nausea"
        ],
        14-26: [
            "Continue prenatal vitamins",
            "Stay active with walking or prenatal yoga",
            "Eat iron-rich foods",
            "Start planning your nursery"
        ],
        27-40: [
            "Monitor baby's movements",
            "Practice relaxation techniques",
            "Prepare your hospital bag",
            "Rest when possible"
        ]
    }
    
    for range_key, tip_list in tips.items():
        if isinstance(range_key, int) and week == range_key:
            return tip_list
        elif isinstance(range_key, tuple) and range_key[0] <= week <= range_key[1]:
            return tip_list
    
    return ["Stay hydrated", "Eat balanced meals", "Get regular checkups", "Listen to your body"]

def get_upcoming_milestones(week):
    """Get upcoming developmental milestones"""
    upcoming = {
        1-12: ["First ultrasound", "Hearing heartbeat", "Completing first trimester"],
        13-26: ["Feeling first movements", "Anatomy scan", "Finding out baby's sex"],
        27-40: ["Third trimester growth scans", "Baby turning head-down", "Preparing for delivery"]
    }
    
    for range_key, milestone_list in upcoming.items():
        if isinstance(range_key, int) and week == range_key:
            return milestone_list
        elif isinstance(range_key, tuple) and range_key[0] <= week <= range_key[1]:
            return milestone_list
    
    return ["Regular prenatal checkups", "Monitoring baby's growth", "Preparing for arrival"]

# Additional views (stubs for now)
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
def clinician_dashboard(request):
    """Dashboard for healthcare providers"""
    if not hasattr(request.user, 'userprofile') or request.user.userprofile.role != UserProfile.Roles.CLINICIAN:
        messages.error(request, 'Access denied. Clinician role required.')
        return redirect('dashboard')
    return render(request, 'pregnancy/clinician_dashboard.html')
