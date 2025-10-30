# pregnancy/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import *
from .forms import *

def home(request):
    """Homepage with dynamic content similar to The Bump"""
    featured_content = EducationalContent.objects.filter(is_active=True)[:3]
    context = {
        'featured_content': featured_content,
        'current_week': 12,  # Example - would be calculated dynamically
    }
    return render(request, 'pregnancy/home.html', context)

@login_required
def dashboard(request):
    """Main dashboard for logged-in users"""
    if request.user.role == 'mother':
        try:
            pregnancy_record = PregnancyRecord.objects.get(mother=request.user)
            vitals = VitalsLog.objects.filter(mother=request.user)[:5]
            appointments = Appointment.objects.filter(mother=request.user, date_time__gte=timezone.now())[:5]
            unread_messages = Message.objects.filter(receiver=request.user, is_read=False).count()
        except PregnancyRecord.DoesNotExist:
            pregnancy_record = None
            vitals = []
            appointments = []
            unread_messages = 0
        
        context = {
            'pregnancy_record': pregnancy_record,
            'vitals': vitals,
            'appointments': appointments,
            'unread_messages': unread_messages,
        }
        return render(request, 'pregnancy/mother_dashboard.html', context)
    
    elif request.user.role == 'clinician':
        # Clinician dashboard
        today_appointments = Appointment.objects.filter(
            clinician=request.user, 
            date_time__date=timezone.now().date()
        )
        patients = User.objects.filter(role='mother')
        
        context = {
            'today_appointments': today_appointments,
            'patients': patients,
        }
        return render(request, 'pregnancy/clinician_dashboard.html', context)
    
    else:
        # Admin dashboard
        return render(request, 'pregnancy/admin_dashboard.html')

@login_required
def track_progress(request):
    """Pregnancy progress tracking"""
    if request.user.role != 'mother':
        return redirect('dashboard')
    
    pregnancy_record = get_object_or_404(PregnancyRecord, mother=request.user)
    weeks_pregnant = (timezone.now().date() - pregnancy_record.pregnancy_start_date).days // 7
    
    # Weekly development information (simplified)
    week_info = {
        'week': weeks_pregnant,
        'baby_size': 'Lime',  # This would come from a database
        'baby_weight': '45g',
        'developments': [
            'Baby\'s reflexes are developing',
            'Fingers and toes are fully separated',
            'Baby is starting to make sucking motions
