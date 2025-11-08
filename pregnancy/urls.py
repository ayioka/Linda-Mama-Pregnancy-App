from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('contact/', views.contact, name='contact'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('track-progress/', views.track_progress, name='track_progress'),
    path('log-vitals/', views.log_vitals, name='log_vitals'),
    path('educational-content/', views.educational_content, name='educational_content'),
    path('content/<slug:slug>/', views.content_detail, name='content_detail'),
    path('appointments/', views.appointments, name='appointments'),
    path('appointments/create/', views.create_appointment, name='create_appointment'),
    path('messaging/', views.messaging, name='messaging'),
    path('conversation/<int:user_id>/', views.conversation, name='conversation'),
    path('emergency-alert/', views.emergency_alert, name='emergency_alert'),
    path('profile/', views.profile, name='profile'),
]
