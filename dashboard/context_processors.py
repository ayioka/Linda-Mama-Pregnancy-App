from pregnancy.models import Pregnancy

def dashboard_data(request):
    """Add dashboard data to all templates"""
    context = {}
    
    if request.user.is_authenticated and request.user.user_type == 'mother':
        active_pregnancy = Pregnancy.objects.filter(
            mother=request.user, 
            is_active=True
        ).first()
        context['active_pregnancy'] = active_pregnancy
    
    return context
