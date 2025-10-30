from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.http import JsonResponse
from .models import *
from .forms import *
from .utils import calculate_pregnancy_progress

def home(request):
    """Homepage view"""
    featured_content = EducationalContent.objects.filter(
        is_featured=True, 
        is_active=True
    )[:6]
    
    context = {
        'featured_content': featured_content,
        'current_week': 12,  # Example week
    }
    return render(request, 'pregnancy/home.html', context)

def about(request):
    """About page view"""
    return render(request, 'pregnancy/about.html')

def services(request):
    """Services page view"""
    return render(request, 'pregnancy/services.html')

def contact(request):
    """Contact page view"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Process contact form (send email, save to database, etc.)
            messages.success(request, 'Thank you for your message! We will get back to you soon.')
            return redirect('contact')
    else:
        form = ContactForm()
    
    return render(request, 'pregnancy/contact.html', {'form': form})

def register(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            
            # If user is a mother, create pregnancy profile
            if user.role == 'mother':
                PregnancyProfile.objects.create(
                    mother=user,
                    last_menstrual_period=form.cleaned_data.get('last_menstrual_period'),
                    blood_type=form.cleaned_data.get('blood_type', '')
                )
            
            messages.success(request, 'Account created successfully! You can now log in.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'pregnancy/register.html', {'form': form})

@login_required
def dashboard(request):
    """Main dashboard view"""
    user = request.user
    
    if user.role == 'mother':
        return mother_dashboard(request)
    elif user.role == 'clinician':
        return clinician_dashboard(request)
    else:
        return admin_dashboard(request)

def mother_dashboard(request):
    """Dashboard for expectant mothers"""
    try:
        pregnancy_profile = PregnancyProfile.objects.get(mother=request.user)
        weeks_pregnant = pregnancy_profile.get_weeks_pregnant()
        days_until_due = pregnancy_profile.get_days_until_due()
    except PregnancyProfile.DoesNotExist:
        pregnancy_profile = None
        weeks_pregnant = 0
        days_until_due = None
    
    # Recent vitals
    recent_vitals = VitalsRecord.objects.filter(mother=request.user)[:5]
    
    # Upcoming appointments
    upcoming_appointments = Appointment.objects.filter(
        mother=request.user,
        scheduled_date__gte=timezone.now(),
        status__in=['scheduled', 'confirmed']
    )[:5]
    
    # Unread messages
    unread_messages = Message.objects.filter(
        receiver=request.user,
        is_read=False
    ).count()
    
    # Recent educational content
    recent_content = EducationalContent.objects.filter(
        is_active=True,
        trimester_target__in=[pregnancy_profile.current_trimester if pregnancy_profile else 'first', 'all']
    )[:3]
    
    context = {
        'pregnancy_profile': pregnancy_profile,
        'weeks_pregnant': weeks_pregnant,
        'days_until_due': days_until_due,
        'recent_vitals': recent_vitals,
        'upcoming_appointments': upcoming_appointments,
        'unread_messages': unread_messages,
        'recent_content': recent_content,
    }
    
    return render(request, 'pregnancy/dashboard_mother.html', context)

def clinician_dashboard(request):
    """Dashboard for healthcare providers"""
    # Today's appointments
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    
    todays_appointments = Appointment.objects.filter(
        clinician=request.user,
        scheduled_date__range=[today_start, today_end],
        status__in=['scheduled', 'confirmed']
    ).order_by('scheduled_date')
    
    # Upcoming appointments
    upcoming_appointments = Appointment.objects.filter(
        clinician=request.user,
        scheduled_date__gte=timezone.now(),
        status__in=['scheduled', 'confirmed']
    ).exclude(scheduled_date__range=[today_start, today_end])[:10]
    
    # Recent patients
    recent_patients = User.objects.filter(
        role='mother',
        mother_appointments__clinician=request.user
    ).distinct()[:5]
    
    # Pending emergency alerts
    pending_alerts = EmergencyAlert.objects.filter(is_responded=False)[:5]
    
    context = {
        'todays_appointments': todays_appointments,
        'upcoming_appointments': upcoming_appointments,
        'recent_patients': recent_patients,
        'pending_alerts': pending_alerts,
    }
    
    return render(request, 'pregnancy/dashboard_clinician.html', context)

def admin_dashboard(request):
    """Dashboard for system administrators"""
    total_users = User.objects.count()
    total_mothers = User.objects.filter(role='mother').count()
    total_clinicians = User.objects.filter(role='clinician').count()
    total_appointments = Appointment.objects.count()
    
    recent_users = User.objects.all()[:5]
    system_stats = {
        'total_users': total_users,
        'total_mothers': total_mothers,
        'total_clinicians': total_clinicians,
        'total_appointments': total_appointments,
    }
    
    context = {
        'system_stats': system_stats,
        'recent_users': recent_users,
    }
    
    return render(request, 'pregnancy/dashboard_admin.html', context)

@login_required
@user_passes_test(lambda u: u.role == 'mother')
def track_progress(request):
    """Pregnancy progress tracking view"""
    pregnancy_profile = get_object_or_404(PregnancyProfile, mother=request.user)
    weeks_pregnant = pregnancy_profile.get_weeks_pregnant()
    
    # Get week-specific information
    week_info = calculate_pregnancy_progress(weeks_pregnant)
    
    # Pregnancy milestones
    milestones = [
        {'week': 12, 'title': 'First Trimester Complete', 'description': 'Risk of miscarriage decreases significantly'},
        {'week': 20, 'title': 'Anatomy Scan', 'description': 'Detailed ultrasound to check baby development'},
        {'week': 28, 'title': 'Third Trimester Begins', 'description': 'Start counting baby movements'},
        {'week': 36, 'title': 'Baby is Full Term', 'description': 'Baby could arrive any time now!'},
    ]
    
    context = {
        'pregnancy_profile': pregnancy_profile,
        'week_info': week_info,
        'milestones': milestones,
        'weeks_pregnant': weeks_pregnant,
    }
    
    return render(request, 'pregnancy/track_progress.html', context)

@login_required
@user_passes_test(lambda u: u.role == 'mother')
def log_vitals(request):
    """Vitals logging view"""
    if request.method == 'POST':
        form = VitalsRecordForm(request.POST)
        if form.is_valid():
            vitals = form.save(commit=False)
            vitals.mother = request.user
            vitals.save()
            messages.success(request, 'Vitals recorded successfully!')
            return redirect('dashboard')
    else:
        form = VitalsRecordForm()
    
    # Recent vitals for reference
    recent_vitals = VitalsRecord.objects.filter(mother=request.user)[:5]
    
    context = {
        'form': form,
        'recent_vitals': recent_vitals,
    }
    
    return render(request, 'pregnancy/log_vitals.html', context)

@login_required
def educational_content(request):
    """Educational content hub"""
    trimester = request.GET.get('trimester', 'all')
    content_type = request.GET.get('type', 'all')
    
    content = EducationalContent.objects.filter(is_active=True)
    
    if trimester != 'all':
        content = content.filter(trimester_target__in=[trimester, 'all'])
    
    if content_type != 'all':
        content = content.filter(content_type=content_type)
    
    # Featured content
    featured_content = content.filter(is_featured=True)
    
    context = {
        'educational_content': content,
        'featured_content': featured_content,
        'selected_trimester': trimester,
        'selected_type': content_type,
    }
    
    return render(request, 'pregnancy/educational_content.html', context)

@login_required
def content_detail(request, slug):
    """Educational content detail view"""
    content = get_object_or_404(EducationalContent, slug=slug, is_active=True)
    
    # Related content
    related_content = EducationalContent.objects.filter(
        is_active=True,
        trimester_target=content.trimester_target
    ).exclude(id=content.id)[:3]
    
    context = {
        'content': content,
        'related_content': related_content,
    }
    
    return render(request, 'pregnancy/content_detail.html', context)

@login_required
def appointments(request):
    """Appointments management view"""
    if request.user.role == 'mother':
        appointments = Appointment.objects.filter(mother=request.user)
    else:
        appointments = Appointment.objects.filter(clinician=request.user)
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        appointments = appointments.filter(status=status_filter)
    
    context = {
        'appointments': appointments,
    }
    
    return render(request, 'pregnancy/appointments.html', context)

@login_required
def messaging(request):
    """Messaging view"""
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.save()
            messages.success(request, 'Message sent successfully!')
            return redirect('messaging')
    else:
        form = MessageForm()
    
    # Get conversations
    sent_messages = Message.objects.filter(sender=request.user)
    received_messages = Message.objects.filter(receiver=request.user)
    
    # Group messages by conversation
    conversations = {}
    all_messages = list(sent_messages) + list(received_messages)
    
    for msg in all_messages:
        other_user = msg.receiver if msg.sender == request.user else msg.sender
        if other_user.id not in conversations:
            conversations[other_user.id] = {
                'user': other_user,
                'last_message': msg,
                'unread_count': Message.objects.filter(
                    sender=other_user,
                    receiver=request.user,
                    is_read=False
                ).count()
            }
    
    context = {
        'form': form,
        'conversations': sorted(conversations.values(), key=lambda x: x['last_message'].created_at, reverse=True),
    }
    
    return render(request, 'pregnancy/messaging.html', context)

@login_required
@user_passes_test(lambda u: u.role == 'mother')
def emergency_alert(request):
    """Emergency alert view"""
    if request.method == 'POST':
        form = EmergencyAlertForm(request.POST)
        if form.is_valid():
            alert = form.save(commit=False)
            alert.mother = request.user
            alert.save()
            
            # Here you would typically send notifications to clinicians
            messages.warning(request, 'Emergency alert sent! Help is on the way.')
            return redirect('dashboard')
    else:
        form = EmergencyAlertForm()
    
    return render(request, 'pregnancy/emergency_alert.html', {'form': form})

# API Views for AJAX functionality
@login_required
def api_week_info(request, week):
    """API endpoint for week-specific information"""
    week_info = calculate_pregnancy_progress(week)
    return JsonResponse(week_info)

@login_required
def api_mark_message_read(request, message_id):
    """API endpoint to mark message as read"""
    message = get_object_or_404(Message, id=message_id, receiver=request.user)
    message.is_read = True
    message.save()
    return JsonResponse({'status': 'success'}))
