from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Q
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging

from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm, AppointmentForm, HealthMetricForm
from .models import UserProfile, User, Appointment, HealthMetric, PregnancyMilestone

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
    """Home page view"""
    if request.user.is_authenticated:
        return redirect_to_role_based_dashboard(request.user)
    return render(request, 'pregnancy/home.html')

def custom_login(request):
    """Custom login view"""
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

def custom_logout(request):
    """Custom logout view"""
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('home')

def redirect_to_role_based_dashboard(user):
    """Redirect user based on their role"""
    try:
        profile = user.userprofile
        if profile.role == UserProfile.Roles.CLINICIAN:
            return redirect('clinician_dashboard')
        elif profile.role == UserProfile.Roles.ADMIN:
            return redirect('admin_dashboard')
        else:
            return redirect('patient_dashboard')
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=user)
        return redirect('patient_dashboard')

def signup(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('patient_dashboard')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
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
    from django.contrib.sites.shortcuts import get_current_site
    current_site = get_current_site(request)
    activation_link = f"http://{current_site.domain}/activate/{uid}/{token}/"
    subject = 'Activate your Linda Mama Pregnancy Tracker Account'
    message = render_to_string('pregnancy/email_activation.txt', {
        'user': user, 
        'activation_link': activation_link, 
        'site_name': current_site.name
    })
    html_message = render_to_string('pregnancy/email_activation.html', {
        'user': user, 
        'activation_link': activation_link, 
        'site_name': current_site.name
    })
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False, html_message=html_message)

def activate(request, uidb64, token):
    """Activate user account"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        if not user.is_active:
            user.is_active = True
            user.save()
        profile, created = UserProfile.objects.get_or_create(user=user)
        login(request, user)
        try:
            send_welcome_email(request, user)
        except Exception as e:
            logger.warning(f"Failed to send welcome email to {user.email}: {str(e)}")
        messages.success(request, 'Your account has been activated successfully!')
        return redirect_to_role_based_dashboard(user)
    else:
        messages.error(request, 'Activation link is invalid or has expired.')
        return redirect('home')

def send_welcome_email(request, user):
    """Send welcome email after activation"""
    from django.contrib.sites.shortcuts import get_current_site
    current_site = get_current_site(request)
    dashboard_url = f"http://{current_site.domain}/dashboard/"
    subject = 'Welcome to Linda Mama Pregnancy Tracker!'
    message = render_to_string('pregnancy/welcome_email.txt', {
        'user': user, 
        'dashboard_url': dashboard_url, 
        'site_name': current_site.name
    })
    html_message = render_to_string('pregnancy/welcome_email.html', {
        'user': user, 
        'dashboard_url': dashboard_url, 
        'site_name': current_site.name
    })
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False, html_message=html_message)

@login_required
@get_user_profile
def patient_dashboard(request, profile):
    """Patient dashboard view"""
    # Pregnancy data
    pregnancy_data = profile.calculate_pregnancy_week()
    current_trimester = profile.get_trimester()
    progress_percentage = profile.get_pregnancy_progress()
    
    # Upcoming appointments
    upcoming_appointments = Appointment.objects.filter(
        user=request.user,
        date_time__gte=timezone.now(),
        is_completed=False
    ).order_by('date_time')[:5]
    
    # Recent health metrics
    recent_metrics = HealthMetric.objects.filter(
        user=request.user
    ).order_by('-date')[:5]
    
    # Current milestone
    current_milestone = profile.get_current_milestone()
    
    context = {
        'profile': profile,
        'pregnancy_data': pregnancy_data,
        'current_trimester': current_trimester,
        'progress_percentage': progress_percentage,
        'upcoming_appointments': upcoming_appointments,
        'recent_metrics': recent_metrics,
        'current_milestone': current_milestone,
    }
    return render(request, 'pregnancy/patient_dashboard.html', context)

@login_required
@get_user_profile
def clinician_dashboard(request, profile):
    """Clinician dashboard view"""
    if not profile.is_clinician():
        messages.error(request, 'Access denied. Clinician role required.')
        return redirect('patient_dashboard')
    
    # Today's appointments
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    todays_appointments = Appointment.objects.filter(
        date_time__range=[today_start, today_end],
        is_completed=False
    ).order_by('date_time')
    
    # Upcoming appointments
    upcoming_appointments = Appointment.objects.filter(
        date_time__gte=timezone.now(),
        is_completed=False
    ).exclude(date_time__range=[today_start, today_end]).order_by('date_time')[:10]
    
    # Recent patients
    recent_patients = UserProfile.objects.filter(
        role=UserProfile.Roles.PATIENT
    ).order_by('-created_at')[:5]
    
    context = {
        'profile': profile,
        'todays_appointments': todays_appointments,
        'upcoming_appointments': upcoming_appointments,
        'recent_patients': recent_patients,
    }
    return render(request, 'pregnancy/clinician_dashboard.html', context)

@login_required
@get_user_profile
def admin_dashboard(request, profile):
    """Admin dashboard view"""
    if not profile.is_admin():
        messages.error(request, 'Access denied. Administrator role required.')
        return redirect('patient_dashboard')
    
    # Statistics
    total_users = User.objects.count()
    total_patients = UserProfile.objects.filter(role=UserProfile.Roles.PATIENT).count()
    total_clinicians = UserProfile.objects.filter(role=UserProfile.Roles.CLINICIAN).count()
    total_appointments = Appointment.objects.count()
    upcoming_appointments = Appointment.objects.filter(
        date_time__gte=timezone.now(),
        is_completed=False
    ).count()
    
    # Recent activity
    recent_users = User.objects.order_by('-date_joined')[:5]
    recent_appointments = Appointment.objects.order_by('-created_at')[:5]
    
    context = {
        'profile': profile,
        'total_users': total_users,
        'total_patients': total_patients,
        'total_clinicians': total_clinicians,
        'total_appointments': total_appointments,
        'upcoming_appointments': upcoming_appointments,
        'recent_users': recent_users,
        'recent_appointments': recent_appointments,
    }
    return render(request, 'pregnancy/admin_dashboard.html', context)

@login_required
@get_user_profile
def profile_view(request, profile):
    """User profile view"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserProfileForm(instance=profile)
    
    context = {
        'profile': profile,
        'form': form,
    }
    return render(request, 'pregnancy/profile.html', context)

@login_required
@get_user_profile
def appointments_list(request, profile):
    """List user appointments"""
    appointments = Appointment.objects.filter(user=request.user).order_by('-date_time')
    
    context = {
        'profile': profile,
        'appointments': appointments,
    }
    return render(request, 'pregnancy/appointments.html', context)

@login_required
@get_user_profile
def appointment_create(request, profile):
    """Create new appointment"""
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.user = request.user
            appointment.save()
            messages.success(request, 'Appointment created successfully!')
            return redirect('appointments_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AppointmentForm()
    
    context = {
        'profile': profile,
        'form': form,
    }
    return render(request, 'pregnancy/appointment_form.html', context)

@login_required
@get_user_profile
def appointment_edit(request, profile, appointment_id):
    """Edit existing appointment"""
    appointment = get_object_or_404(Appointment, id=appointment_id, user=request.user)
    
    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Appointment updated successfully!')
            return redirect('appointments_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AppointmentForm(instance=appointment)
    
    context = {
        'profile': profile,
        'form': form,
        'appointment': appointment,
    }
    return render(request, 'pregnancy/appointment_form.html', context)

@login_required
@get_user_profile
def appointment_delete(request, profile, appointment_id):
    """Delete appointment"""
    appointment = get_object_or_404(Appointment, id=appointment_id, user=request.user)
    
    if request.method == 'POST':
        appointment.delete()
        messages.success(request, 'Appointment deleted successfully!')
        return redirect('appointments_list')
    
    context = {
        'profile': profile,
        'appointment': appointment,
    }
    return render(request, 'pregnancy/appointment_confirm_delete.html', context)

@login_required
@get_user_profile
def health_metrics_list(request, profile):
    """List health metrics"""
    metrics = HealthMetric.objects.filter(user=request.user).order_by('-date')
    
    context = {
        'profile': profile,
        'metrics': metrics,
    }
    return render(request, 'pregnancy/health_metrics.html', context)

@login_required
@get_user_profile
def health_metric_create(request, profile):
    """Create new health metric"""
    if request.method == 'POST':
        form = HealthMetricForm(request.POST)
        if form.is_valid():
            metric = form.save(commit=False)
            metric.user = request.user
            
            # Check if metric already exists for this date
            if HealthMetric.objects.filter(user=request.user, date=metric.date).exists():
                messages.error(request, 'Health metric for this date already exists.')
            else:
                metric.save()
                messages.success(request, 'Health metric recorded successfully!')
                return redirect('health_metrics_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = HealthMetricForm()
    
    context = {
        'profile': profile,
        'form': form,
    }
    return render(request, 'pregnancy/health_metric_form.html', context)

@login_required
@get_user_profile
def health_metric_edit(request, profile, metric_id):
    """Edit health metric"""
    metric = get_object_or_404(HealthMetric, id=metric_id, user=request.user)
    
    if request.method == 'POST':
        form = HealthMetricForm(request.POST, instance=metric)
        if form.is_valid():
            form.save()
            messages.success(request, 'Health metric updated successfully!')
            return redirect('health_metrics_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = HealthMetricForm(instance=metric)
    
    context = {
        'profile': profile,
        'form': form,
        'metric': metric,
    }
    return render(request, 'pregnancy/health_metric_form.html', context)

@login_required
@get_user_profile
def pregnancy_milestones(request, profile):
    """Pregnancy milestones view"""
    milestones = PregnancyMilestone.objects.all()
    current_milestone = profile.get_current_milestone()
    
    context = {
        'profile': profile,
        'milestones': milestones,
        'current_milestone': current_milestone,
    }
    return render(request, 'pregnancy/milestones.html', context)

@login_required
@get_user_profile
def milestone_detail(request, profile, week):
    """Pregnancy milestone detail view"""
    milestone = get_object_or_404(PregnancyMilestone, week=week)
    
    context = {
        'profile': profile,
        'milestone': milestone,
    }
    return render(request, 'pregnancy/milestone_detail.html', context)

@login_required
def clinician_patients(request):
    """Clinician's patient list"""
    profile = request.user.userprofile
    if not profile.is_clinician():
        messages.error(request, 'Access denied. Clinician role required.')
        return redirect('patient_dashboard')
    
    patients = UserProfile.objects.filter(role=UserProfile.Roles.PATIENT).order_by('-created_at')
    
    context = {
        'profile': profile,
        'patients': patients,
    }
    return render(request, 'pregnancy/clinician_patients.html', context)

@login_required
def clinician_patient_detail(request, patient_id):
    """Clinician's patient detail view"""
    profile = request.user.userprofile
    if not profile.is_clinician():
        messages.error(request, 'Access denied. Clinician role required.')
        return redirect('patient_dashboard')
    
    patient_profile = get_object_or_404(UserProfile, id=patient_id, role=UserProfile.Roles.PATIENT)
    appointments = Appointment.objects.filter(user=patient_profile.user).order_by('-date_time')[:10]
    health_metrics = HealthMetric.objects.filter(user=patient_profile.user).order_by('-date')[:10]
    
    context = {
        'profile': profile,
        'patient_profile': patient_profile,
        'appointments': appointments,
        'health_metrics': health_metrics,
    }
    return render(request, 'pregnancy/clinician_patient_detail.html', context)

def handler404(request, exception):
    """Custom 404 error handler"""
    return render(request, 'pregnancy/404.html', status=404)

def handler500(request):
    """Custom 500 error handler"""
    return render(request, 'pregnancy/500.html', status=500)
