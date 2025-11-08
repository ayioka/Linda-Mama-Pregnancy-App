from django.urls import path
from . import views

urlpatterns = [
    path('resources/', views.resources, name='resources'),
    path('week-tracker/', views.week_tracker, name='week_tracker'),
    path('health-metrics/', views.health_metrics, name='health_metrics'),
    path('appointments/', views.appointments, name='appointments'),
    path('emergency/', views.emergency, name='emergency'),
    path('nutrition/', views.nutrition, name='nutrition'),
    path('exercise/', views.exercise, name='exercise'),
    path('mental-health/', views.mental_health, name='mental_health'),
    path('baby-development/', views.baby_development, name='baby_development'),
]
