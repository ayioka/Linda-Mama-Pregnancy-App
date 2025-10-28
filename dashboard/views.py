from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from pregnancy.models import Pregnancy, HealthMetric
from appointments.models import Appointment
from messaging.models import Message

def home(request):
    """Landing page for non-authenticated users"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'dashboard/home.html')

@login_required
def dashboard(request):
    """Main dashboard for authenticated users"""
    context = {}
    
    if request.user.user_type == 'mother':
        # Get active pregnancy
        try:
            pregnancy = Pregnancy.objects.filter(mother=request.user, is_active=True).first()
            context['pregnancy'] = pregnancy
            
            if pregnancy:
                # Get recent health metrics
                recent_metrics = HealthMetric.objects.filter(pregnancy=pregnancy)[:5]
                context['recent_metrics'] = recent_metrics
                
                # Get upcoming appointments
                upcoming_appointments = Appointment.objects.filter(
                    pregnancy=pregnancy,
                    date_time__gte=timezone.now()
                ).order_by('date_time')[:5]
                context['upcoming_appointments'] = upcoming_appointments
                
                # Get unread messages
                unread_messages = Message.objects.filter(
                    recipient=request.user,
                    is_read=False
                ).count()
                context['unread_messages'] = unread_messages
                
    elif request.user.user_type == 'clinician':
        # Get clinician's upcoming appointments
        upcoming_appointments = Appointment.objects.filter(
            clinician=request.user,
            date_time__gte=timezone.now()
        ).order_by('date_time')[:10]
        context['upcoming_appointments'] = upcoming_appointments
        
        # Get recent messages
        recent_messages = Message.objects.filter(
            recipient=request.user
        ).order_by('-timestamp')[:5]
        context['recent_messages'] = recent_messages
    
    return render(request, 'dashboard/dashboard.html', context)
