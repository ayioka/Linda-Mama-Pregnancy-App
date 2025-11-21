from django.urls import path
from . import views

urlpatterns = [
    # Authentication URLs
    path('', views.home, name='home'),
    path('login/', views.custom_login, name='login'),
    path('register/', views.signup, name='register'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    
    # Main Application URLs
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('baby-development/', views.baby_development, name='baby_development'),
    
    # Feature URLs
    path('resources/', views.resources, name='resources'),
    path('week-tracker/', views.week_tracker, name='week_tracker'),
    path('health-metrics/', views.health_metrics, name='health_metrics'),
    path('appointments/', views.appointments, name='appointments'),
    path('emergency/', views.emergency, name='emergency'),
    path('nutrition/', views.nutrition, name='nutrition'),
    path('exercise/', views.exercise, name='exercise'),
    path('mental-health/', views.mental_health, name='mental_health'),
    
    # Clinician URLs
    path('clinician/dashboard/', views.clinician_dashboard, name='clinician_dashboard'),
]
