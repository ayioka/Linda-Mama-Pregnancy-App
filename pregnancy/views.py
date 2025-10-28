from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Pregnancy, HealthMetric
from .forms import PregnancyForm, HealthMetricForm

@login_required
def pregnancy_create(request):
    if request.user.user_type != 'mother':
        messages.error(request, 'Only expectant mothers can create pregnancy records.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = PregnancyForm(request.POST)
        if form.is_valid():
            pregnancy = form.save(commit=False)
            pregnancy.mother = request.user
            pregnancy.save()
            messages.success(request, 'Pregnancy record created successfully!')
            return redirect('pregnancy:pregnancy_detail', pk=pregnancy.pk)
    else:
        form = PregnancyForm()
    
    return render(request, 'pregnancy/pregnancy_create.html', {'form': form})

@login_required
def pregnancy_detail(request, pk):
    pregnancy = get_object_or_404(Pregnancy, pk=pk, mother=request.user)
    
    # Health metrics for chart
    health_metrics = HealthMetric.objects.filter(pregnancy=pregnancy).order_by('date_recorded')[:10]
    
    context = {
        'pregnancy': pregnancy,
        'health_metrics': health_metrics,
    }
    return render(request, 'pregnancy/pregnancy_detail.html', context)

@login_required
def health_metrics_log(request, pregnancy_pk):
    pregnancy = get_object_or_404(Pregnancy, pk=pregnancy_pk, mother=request.user)
    
    if request.method == 'POST':
        form = HealthMetricForm(request.POST)
        if form.is_valid():
            health_metric = form.save(commit=False)
            health_metric.pregnancy = pregnancy
            health_metric.save()
            messages.success(request, 'Health metrics recorded successfully!')
            return redirect('pregnancy:pregnancy_detail', pk=pregnancy.pk)
    else:
        form = HealthMetricForm()
    
    recent_metrics = HealthMetric.objects.filter(pregnancy=pregnancy).order_by('-date_recorded')[:5]
    
    context = {
        'pregnancy': pregnancy,
        'form': form,
        'recent_metrics': recent_metrics,
    }
    return render(request, 'pregnancy/health_metrics.html', context)
