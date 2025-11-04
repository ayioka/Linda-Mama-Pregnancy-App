# pregnancy/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta
import json

from .models import User, PregnancyProfile, VitalsRecord, Appointment, Message, EmergencyAlert, EducationalContent
from .forms import UserRegistrationForm, UserProfileForm, PregnancyProfileForm, VitalsRecordForm, AppointmentForm, MessageForm, EmergencyAlertForm

# Public pages
def home(request):
    """Home page view"""
    context = {
        'featured_content': EducationalContent.objects.filter(is_featured=True, is_active=True)[:3]
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
    return render(request, 'pregnancy/contact.html')

# Authentication
def register(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'pregnancy/register.html', {'form': form})

# Dashboard and main features
@login_required
def dashboard(request):
    """User dashboard view"""
    context = {}
    
    if request.user.role == 'mother':
        # Mother-specific dashboard data
        try:
            pregnancy_profile = PregnancyProfile.objects.get(mother=request.user)
            context['pregnancy_profile'] = pregnancy_profile
            context['weeks_pregnant'] = pregnancy_profile.get_weeks_pregnant()
            context['days_until_due'] = pregnancy_profile.get_days_until_due()
        except PregnancyProfile.DoesNotExist:
            context['pregnancy_profile'] = None
        
        # Recent vitals
        context['recent_vitals'] = VitalsRecord.objects.filter(mother=request.user).order_by('-record_date')[:5]
        
        # Upcoming appointments
        context['upcoming_appointments'] = Appointment.objects.filter(
            mother=request.user,
            scheduled_date__gte=timezone.now(),
            status__in=['scheduled', 'confirmed']
        ).order_by('scheduled_date')[:3]
        
        # Unread messages
        context['unread_messages_count'] = Message.objects.filter(
            receiver=request.user,
            is_read=False
        ).count()
        
    elif request.user.role == 'clinician':
        # Clinician-specific dashboard data
        context['today_appointments'] = Appointment.objects.filter(
            clinician=request.user,
            scheduled_date__date=timezone.now().date(),
            status__in=['scheduled', 'confirmed']
        ).order_by('scheduled_date')
        
        context['pending_alerts'] = EmergencyAlert.objects.filter(
            is_responded=False
        ).order_by('-created_at')[:5]
        
        context['patient_count'] = User.objects.filter(role='mother').count()
    
    # Recent educational content for all users
    context['recent_content'] = EducationalContent.objects.filter(
        is_active=True
    ).order_by('-created_at')[:3]
    
    return render(request, 'pregnancy/dashboard.html', context)

@login_required
def profile(request):
    """User profile management view"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    # Handle pregnancy profile for mothers
    pregnancy_profile = None
    pregnancy_form = None
    
    if request.user.role == 'mother':
        try:
            pregnancy_profile = PregnancyProfile.objects.get(mother=request.user)
            pregnancy_form = PregnancyProfileForm(instance=pregnancy_profile)
        except PregnancyProfile.DoesNotExist:
            pregnancy_form = PregnancyProfileForm()
    
    if request.method == 'POST' and 'pregnancy_data' in request.POST:
        pregnancy_form = PregnancyProfileForm(request.POST)
        if pregnancy_form.is_valid():
            pregnancy_profile = pregnancy_form.save(commit=False)
            pregnancy_profile.mother = request.user
            pregnancy_profile.save()
            messages.success(request, 'Pregnancy information updated successfully!')
            return redirect('profile')
    
    context = {
        'form': form,
        'pregnancy_profile': pregnancy_profile,
        'pregnancy_form': pregnancy_form,
    }
    
    return render(request, 'pregnancy/profile.html', context)

@login_required
def track_progress(request):
    """Pregnancy progress tracking view"""
    if request.user.role != 'mother':
        return HttpResponseForbidden("This page is for expectant mothers only.")
    
    try:
        pregnancy_profile = PregnancyProfile.objects.get(mother=request.user)
        weeks_pregnant = pregnancy_profile.get_weeks_pregnant()
        
        # Sample week data - in a real app, this would come from a database
        week_info = get_week_info(weeks_pregnant)
        milestones = get_pregnancy_milestones()
        
        context = {
            'pregnancy_profile': pregnancy_profile,
            'weeks_pregnant': weeks_pregnant,
            'week_info': week_info,
            'milestones': milestones,
            'days_until_due': pregnancy_profile.get_days_until_due(),
        }
        
    except PregnancyProfile.DoesNotExist:
        messages.warning(request, 'Please complete your pregnancy profile to track your progress.')
        return redirect('profile')
    
    return render(request, 'pregnancy/track_progress.html', context)

@login_required
def log_vitals(request):
    """Vitals logging view"""
    if request.user.role != 'mother':
        return HttpResponseForbidden("This page is for expectant mothers only.")
    
    if request.method == 'POST':
        form = VitalsRecordForm(request.POST)
        if form.is_valid():
            vitals_record = form.save(commit=False)
            vitals_record.mother = request.user
            vitals_record.save()
            messages.success(request, 'Vitals recorded successfully!')
            return redirect('log_vitals')
    else:
        form = VitalsRecordForm()
    
    # Get recent vitals for display
    recent_vitals = VitalsRecord.objects.filter(mother=request.user).order_by('-record_date')[:10]
    
    context = {
        'form': form,
        'recent_vitals': recent_vitals,
    }
    
    return render(request, 'pregnancy/log_vitals.html', context)

@login_required
def educational_content(request):
    """Educational content library view"""
    content_type = request.GET.get('type', 'all')
    trimester = request.GET.get('trimester', 'all')
    
    # Base queryset
    content = EducationalContent.objects.filter(is_active=True)
    
    # Apply filters
    if content_type != 'all':
        content = content.filter(content_type=content_type)
    
    if trimester != 'all':
        content = content.filter(trimester_target=trimester)
    
    # Get featured content
    featured_content = EducationalContent.objects.filter(
        is_featured=True, 
        is_active=True
    )[:2]
    
    context = {
        'educational_content': content,
        'featured_content': featured_content,
        'selected_type': content_type,
        'selected_trimester': trimester,
    }
    
    return render(request, 'pregnancy/educational_content.html', context)

@login_required
def content_detail(request, slug):
    """Individual educational content detail view"""
    content = get_object_or_404(EducationalContent, slug=slug, is_active=True)
    
    # Increment view count (you might want to add this field to your model)
    # content.view_count += 1
    # content.save()
    
    # Get related content
    related_content = EducationalContent.objects.filter(
        trimester_target=content.trimester_target,
        is_active=True
    ).exclude(id=content.id)[:3]
    
    context = {
        'content': content,
        'related_content': related_content,
    }
    
    return render(request, 'pregnancy/content_detail.html', context)

@login_required
def appointments(request):
    """Appointments management view"""
    status_filter = request.GET.get('status', '')
    
    if request.user.role == 'mother':
        appointments_list = Appointment.objects.filter(mother=request.user)
    elif request.user.role == 'clinician':
        appointments_list = Appointment.objects.filter(clinician=request.user)
    else:
        appointments_list = Appointment.objects.none()
    
    # Apply status filter
    if status_filter:
        appointments_list = appointments_list.filter(status=status_filter)
    
    # Get upcoming appointments for the card
    upcoming_appointments = appointments_list.filter(
        scheduled_date__gte=timezone.now(),
        status__in=['scheduled', 'confirmed']
    ).order_by('scheduled_date')[:6]
    
    context = {
        'appointments': appointments_list.order_by('-scheduled_date'),
        'upcoming_appointments': upcoming_appointments,
        'status_filter': status_filter,
    }
    
    return render(request, 'pregnancy/appointments.html', context)

@login_required
def create_appointment(request):
    """Create new appointment view"""
    if request.method == 'POST':
        form = AppointmentForm(request.POST, user=request.user)
        if form.is_valid():
            appointment = form.save(commit=False)
            
            if request.user.role == 'mother':
                appointment.mother = request.user
            elif request.user.role == 'clinician':
                # Clinicians can create appointments for mothers
                appointment.clinician = request.user
            
            appointment.save()
            messages.success(request, 'Appointment scheduled successfully!')
            return redirect('appointments')
    else:
        form = AppointmentForm(user=request.user)
    
    context = {
        'form': form,
    }
    
    return render(request, 'pregnancy/create_appointment.html', context)

@login_required
def update_appointment(request, appointment_id):
    """Update appointment view"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check permissions
    if request.user not in [appointment.mother, appointment.clinician]:
        return HttpResponseForbidden("You don't have permission to edit this appointment.")
    
    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Appointment updated successfully!')
            return redirect('appointments')
    else:
        form = AppointmentForm(instance=appointment, user=request.user)
    
    context = {
        'form': form,
        'appointment': appointment,
    }
    
    return render(request, 'pregnancy/update_appointment.html', context)

@login_required
def cancel_appointment(request, appointment_id):
    """Cancel appointment view"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check permissions
    if request.user not in [appointment.mother, appointment.clinician]:
        return HttpResponseForbidden("You don't have permission to cancel this appointment.")
    
    if request.method == 'POST':
        appointment.status = 'cancelled'
        appointment.save()
        messages.success(request, 'Appointment cancelled successfully!')
        return redirect('appointments')
    
    context = {
        'appointment': appointment,
    }
    
    return render(request, 'pregnancy/cancel_appointment.html', context)

@login_required
def messaging(request):
    """Messaging inbox view"""
    # Get conversations (users you've exchanged messages with)
    sent_messages = Message.objects.filter(sender=request.user).values('receiver').distinct()
    received_messages = Message.objects.filter(receiver=request.user).values('sender').distinct()
    
    user_ids = set()
    for msg in sent_messages:
        user_ids.add(msg['receiver'])
    for msg in received_messages:
        user_ids.add(msg['sender'])
    
    conversations = []
    for user_id in user_ids:
        user = User.objects.get(id=user_id)
        last_message = Message.objects.filter(
            Q(sender=request.user, receiver=user) | Q(sender=user, receiver=request.user)
        ).order_by('-created_at').first()
        
        unread_count = Message.objects.filter(
            sender=user, receiver=request.user, is_read=False
        ).count()
        
        conversations.append({
            'user': user,
            'last_message': last_message,
            'unread_count': unread_count,
        })
    
    # Sort conversations by last message time
    conversations.sort(key=lambda x: x['last_message'].created_at if x['last_message'] else timezone.make_aware(datetime.min), reverse=True)
    
    context = {
        'conversations': conversations,
    }
    
    return render(request, 'pregnancy/messaging.html', context)

@login_required
def conversation(request, user_id):
    """Individual conversation view"""
    other_user = get_object_or_404(User, id=user_id)
    
    # Get messages between current user and other user
    messages = Message.objects.filter(
        Q(sender=request.user, receiver=other_user) | 
        Q(sender=other_user, receiver=request.user)
    ).order_by('created_at')
    
    # Mark messages as read
    Message.objects.filter(sender=other_user, receiver=request.user, is_read=False).update(is_read=True)
    
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.receiver = other_user
            message.save()
            return redirect('conversation', user_id=user_id)
    else:
        form = MessageForm()
    
    context = {
        'other_user': other_user,
        'messages': messages,
        'form': form,
    }
    
    return render(request, 'pregnancy/conversation.html', context)

@login_required
def send_message(request):
    """Send message view (AJAX or regular)"""
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success', 'message_id': str(message.id)})
            else:
                messages.success(request, 'Message sent successfully!')
                return redirect('messaging')
    
    # If not AJAX, redirect back to messaging
    return redirect('messaging')

@login_required
def emergency_alert(request):
    """Emergency alert creation view"""
    if request.user.role != 'mother':
        return HttpResponseForbidden("This page is for expectant mothers only.")
    
    if request.method == 'POST':
        form = EmergencyAlertForm(request.POST)
        if form.is_valid():
            alert = form.save(commit=False)
            alert.mother = request.user
            alert.save()
            
            # In a real application, you would send notifications to clinicians here
            messages.success(request, 'Emergency alert sent! Healthcare providers have been notified.')
            return redirect('dashboard')
    else:
        form = EmergencyAlertForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'pregnancy/emergency_alert.html', context)

# API endpoints
@login_required
def api_week_info(request, week):
    """API endpoint for week-by-week pregnancy information"""
    if request.user.role != 'mother':
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    week_info = get_week_info(week)
    
    return JsonResponse(week_info)

@login_required
def api_mark_message_read(request, message_id):
    """API endpoint to mark message as read"""
    try:
        message = Message.objects.get(id=message_id, receiver=request.user)
        message.is_read = True
        message.save()
        return JsonResponse({'status': 'success'})
    except Message.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Message not found'}, status=404)

# Helper functions
def get_week_info(week):
    """Helper function to get week-by-week pregnancy information"""
    # This would typically come from a database
    week_data = {
        18: {
            'week': 18,
            'baby_size': 'Bell Pepper',
            'baby_length': 'About 5.5 inches (14 cm)',
            'baby_weight': 'About 7 ounces (200 grams)',
            'developments': [
                'Your baby\'s ears are now in their final position',
                'Bones are hardening, especially the leg bones and inner ear',
                'Your baby is practicing swallowing and sucking',
                'The nervous system is rapidly maturing',
                'Unique fingerprints are forming on fingertips'
            ],
            'mother_changes': [
                'You may start feeling your baby move (quickening)',
                'Increased appetite as nausea typically subsides',
                'Your uterus is now about the size of a cantaloupe',
                'You might experience some lower back discomfort',
                'Skin changes like the "pregnancy glow" may appear'
            ],
            'tips': [
                'Start sleeping on your side to improve circulation',
                'Consider prenatal yoga or gentle stretching exercises',
                'Stay hydrated to help with swelling and digestion',
                'Begin researching childbirth education classes',
                'Track your baby\'s movements when you feel them'
            ],
            'medical_checkups': [
                'Your mid-pregnancy ultrasound is typically between 18-22 weeks',
                'Discuss any unusual symptoms with your healthcare provider',
                'Monitor your blood pressure regularly'
            ]
        }
        # Add more weeks as needed...
    }
    
    return week_data.get(week, {
        'week': week,
        'baby_size': 'Developing',
        'baby_length': 'Growing',
        'baby_weight': 'Increasing',
        'developments': ['Your baby is developing week by week.'],
        'mother_changes': ['Your body is adapting to support your growing baby.'],
        'tips': ['Continue with regular prenatal care and healthy habits.'],
        'medical_checkups': ['Follow your healthcare provider\'s schedule.']
    })

def get_pregnancy_milestones():
    """Helper function to get pregnancy milestones"""
    return [
        {'week': 4, 'title': 'Positive Pregnancy Test', 'description': 'Confirmed your pregnancy'},
        {'week': 8, 'title': 'First Ultrasound', 'description': 'Saw your baby for the first time'},
        {'week': 12, 'title': 'End of First Trimester', 'description': 'Completed the first 12 weeks'},
        {'week': 16, 'title': 'Feeling Baby Move', 'description': 'First sensations of baby movement'},
        {'week': 20, 'title': 'Anatomy Scan', 'description': 'Detailed ultrasound to check baby\'s development'},
        {'week': 24, 'title': 'Viability Milestone', 'description': 'Baby has a chance of survival if born early'},
        {'week': 28, 'title': 'Third Trimester Begins', 'description': 'Entered the final trimester'},
        {'week': 32, 'title': 'Baby Positioning', 'description': 'Baby may settle into head-down position'},
        {'week': 36, 'title': 'Full Term', 'description': 'Baby is considered full term'},
        {'week': 40, 'title': 'Due Date', 'description': 'Expected arrival of your baby'},
    ]
