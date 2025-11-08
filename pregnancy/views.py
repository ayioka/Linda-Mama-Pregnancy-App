from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.http import JsonResponse
from datetime import timedelta

from .models import *
from .forms import *
from .utils import calculate_pregnancy_progress


# -------------------- Public Views -------------------- #
def home(request):
    featured_content = EducationalContent.objects.filter(is_featured=True, is_active=True)[:6]
    context = {
        'featured_content': featured_content,
        'current_week': 12,
    }
    return render(request, 'pregnancy/home.html', context)


def about(request):
    return render(request, 'pregnancy/about.html')


def services(request):
    return render(request, 'pregnancy/services.html')


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            messages.success(request, 'Thank you for your message! We will get back to you soon.')
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'pregnancy/contact.html', {'form': form})


# -------------------- Authentication -------------------- #
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            if user.role == 'mother':
                PregnancyProfile.objects.create(
                    mother=user,
                    last_menstrual_period=form.cleaned_data.get('last_menstrual_period'),
                    blood_type=form.cleaned_data.get('blood_type', '')
                )
            login(request, user)
            messages.success(request, f'Account created successfully! Welcome, {user.first_name}!')
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'pregnancy/register.html', {'form': form})


# -------------------- Dashboard Views -------------------- #
@login_required
def dashboard(request):
    user = request.user
    if user.role == 'mother':
        return mother_dashboard(request)
    elif user.role == 'clinician':
        return clinician_dashboard(request)
    else:
        return admin_dashboard(request)


def mother_dashboard(request):
    pregnancy_profile = PregnancyProfile.objects.filter(mother=request.user).first()
    weeks_pregnant = pregnancy_profile.get_weeks_pregnant() if pregnancy_profile else 0
    days_until_due = pregnancy_profile.get_days_until_due() if pregnancy_profile else None
    recent_vitals = VitalsRecord.objects.filter(mother=request.user)[:5]
    upcoming_appointments = Appointment.objects.filter(
        mother=request.user,
        scheduled_date__gte=timezone.now(),
        status__in=['scheduled', 'confirmed']
    )[:5]
    unread_messages = Message.objects.filter(receiver=request.user, is_read=False).count()
    recent_content = EducationalContent.objects.filter(is_active=True)[:3]

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
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    todays_appointments = Appointment.objects.filter(
        clinician=request.user,
        scheduled_date__range=[today_start, today_end],
        status__in=['scheduled', 'confirmed']
    ).order_by('scheduled_date')

    upcoming_appointments = Appointment.objects.filter(
        clinician=request.user,
        scheduled_date__gte=timezone.now(),
        status__in=['scheduled', 'confirmed']
    ).exclude(scheduled_date__range=[today_start, today_end])[:10]

    recent_patients = User.objects.filter(
        role='mother',
        mother_appointments__clinician=request.user
    ).distinct()[:5]

    pending_alerts = EmergencyAlert.objects.filter(is_responded=False)[:5]

    context = {
        'todays_appointments': todays_appointments,
        'upcoming_appointments': upcoming_appointments,
        'recent_patients': recent_patients,
        'pending_alerts': pending_alerts,
    }
    return render(request, 'pregnancy/dashboard_clinician.html', context)


def admin_dashboard(request):
    context = {
        'system_stats': {
            'total_users': User.objects.count(),
            'total_mothers': User.objects.filter(role='mother').count(),
            'total_clinicians': User.objects.filter(role='clinician').count(),
            'total_appointments': Appointment.objects.count(),
        },
        'recent_users': User.objects.all().order_by('-date_joined')[:5],
    }
    return render(request, 'pregnancy/dashboard_admin.html', context)


# -------------------- Mother Functions -------------------- #
@login_required
@user_passes_test(lambda u: u.role == 'mother')
def track_progress(request):
    pregnancy_profile = PregnancyProfile.objects.filter(mother=request.user).first()
    if not pregnancy_profile:
        messages.warning(request, 'Please complete your pregnancy profile to track your progress.')
        return redirect('profile')

    weeks_pregnant = pregnancy_profile.get_weeks_pregnant()
    week_info = calculate_pregnancy_progress(weeks_pregnant)
    milestones = [
        {'week': 12, 'title': 'First Trimester Complete', 'description': 'Risk of miscarriage decreases'},
        {'week': 20, 'title': 'Anatomy Scan', 'description': 'Detailed ultrasound'},
        {'week': 28, 'title': 'Third Trimester Begins', 'description': 'Start counting baby movements'},
        {'week': 36, 'title': 'Baby is Full Term', 'description': 'Baby could arrive any time now!'},
    ]
    return render(request, 'pregnancy/track_progress.html', {
        'pregnancy_profile': pregnancy_profile,
        'week_info': week_info,
        'milestones': milestones,
        'weeks_pregnant': weeks_pregnant
    })


@login_required
@user_passes_test(lambda u: u.role == 'mother')
def log_vitals(request):
    form = VitalsRecordForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        vitals = form.save(commit=False)
        vitals.mother = request.user
        vitals.save()
        messages.success(request, 'Vitals recorded successfully!')
        return redirect('dashboard')

    recent_vitals = VitalsRecord.objects.filter(mother=request.user)[:5]
    return render(request, 'pregnancy/log_vitals.html', {'form': form, 'recent_vitals': recent_vitals})


# -------------------- Educational Content -------------------- #
@login_required
def educational_content(request):
    trimester = request.GET.get('trimester', 'all')
    content_type = request.GET.get('type', 'all')
    content = EducationalContent.objects.filter(is_active=True)

    if trimester != 'all':
        content = content.filter(trimester_target__in=[trimester, 'all'])
    if content_type != 'all':
        content = content.filter(content_type=content_type)

    return render(request, 'pregnancy/educational_content.html', {
        'educational_content': content,
        'featured_content': content.filter(is_featured=True),
        'selected_trimester': trimester,
        'selected_type': content_type
    })


@login_required
def content_detail(request, slug):
    content = get_object_or_404(EducationalContent, slug=slug, is_active=True)
    related_content = EducationalContent.objects.filter(is_active=True, trimester_target=content.trimester_target).exclude(id=content.id)[:3]
    return render(request, 'pregnancy/content_detail.html', {'content': content, 'related_content': related_content})


# -------------------- Appointments -------------------- #
@login_required
def appointments(request):
    appointments = Appointment.objects.filter(
        mother=request.user if request.user.role == 'mother' else None
    ) or Appointment.objects.filter(
        clinician=request.user if request.user.role == 'clinician' else None
    )
    status_filter = request.GET.get('status')
    if status_filter:
        appointments = appointments.filter(status=status_filter)
    return render(request, 'pregnancy/appointments.html', {'appointments': appointments})


@login_required
def create_appointment(request):
    form = AppointmentForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        appointment = form.save(commit=False)
        if request.user.role == 'mother':
            appointment.mother = request.user
        appointment.save()
        messages.success(request, 'Appointment scheduled successfully!')
        return redirect('appointments')
    return render(request, 'pregnancy/create_appointment.html', {'form': form})


# -------------------- Messaging -------------------- #
@login_required
def messaging(request):
    sent_messages = Message.objects.filter(sender=request.user)
    received_messages = Message.objects.filter(receiver=request.user)
    all_messages = list(sent_messages) + list(received_messages)

    conversations = {}
    for msg in all_messages:
        other_user = msg.receiver if msg.sender == request.user else msg.sender
        if other_user.id not in conversations:
            conversations[other_user.id] = {
                'user': other_user,
                'last_message': msg,
                'unread_count': Message.objects.filter(sender=other_user, receiver=request.user, is_read=False).count()
            }

    form = MessageForm(request.POST or None, user=request.user)
    if request.method == 'POST' and form.is_valid():
        message = form.save(commit=False)
        message.sender = request.user
        message.save()
        return redirect('messaging')

    return render(request, 'pregnancy/messaging.html', {
        'form': form,
        'conversations': sorted(conversations.values(), key=lambda x: x['last_message'].created_at, reverse=True)
    })


@login_required
def conversation(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    messages_qs = Message.objects.filter(
        Q(sender=request.user, receiver=other_user) |
        Q(sender=other_user, receiver=request.user)
    ).order_by('created_at')

    Message.objects.filter(sender=other_user, receiver=request.user, is_read=False).update(is_read=True)
    form = MessageForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        msg = form.save(commit=False)
        msg.sender = request.user
        msg.receiver = other_user
        msg.save()
        return redirect('conversation', user_id=user_id)

    return render(request, 'pregnancy/conversation.html', {'other_user': other_user, 'messages': messages_qs, 'form': form})


# -------------------- Emergency Alerts -------------------- #
@login_required
@user_passes_test(lambda u: u.role == 'mother')
def emergency_alert(request):
    form = EmergencyAlertForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        alert = form.save(commit=False)
        alert.mother = request.user
        alert.save()
        messages.warning(request, 'Emergency alert sent!')
        return redirect('dashboard')
    return render(request, 'pregnancy/emergency_alert.html', {'form': form})


# -------------------- Profile -------------------- #
@login_required
def profile(request):
    form = UserUpdateForm(request.POST or None, request.FILES or None, instance=request.user)
    try:
        pregnancy_profile = PregnancyProfile.objects.get(mother=request.user)
        pregnancy_form = PregnancyProfileForm(request.POST or None, instance=pregnancy_profile)
    except PregnancyProfile.DoesNotExist:
        pregnancy_profile = None
        pregnancy_form = PregnancyProfileForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid() and pregnancy_form.is_valid():
            form.save()
            pregnancy_profile = pregnancy_form.save(commit=False)
            pregnancy_profile.mother = request.user
            pregnancy_profile.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')

    return render(request, 'pregnancy/profile.html', {
        'form': form,
        'pregnancy_profile': pregnancy_profile,
        'pregnancy_form': pregnancy_form
    })
