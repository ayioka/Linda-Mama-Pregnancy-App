from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Public pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('contact/', views.contact, name='contact'),
    
    # Authentication
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='pregnancy/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Password reset
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(template_name='pregnancy/password_reset.html'), 
         name='password_reset'),
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='pregnancy/password_reset_done.html'), 
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='pregnancy/password_reset_confirm.html'), 
         name='password_reset_confirm'),
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='pregnancy/password_reset_complete.html'), 
         name='password_reset_complete'),
    
    # Dashboard and main features
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('track-progress/', views.track_progress, name='track_progress'),
    path('log-vitals/', views.log_vitals, name='log_vitals'),
    path('educational-content/', views.educational_content, name='educational_content'),
    path('content/<slug:slug>/', views.content_detail, name='content_detail'),
    path('appointments/', views.appointments, name='appointments'),
    path('messaging/', views.messaging, name='messaging'),
    path('emergency-alert/', views.emergency_alert, name='emergency_alert'),
    
    # API endpoints
    path('api/week-info/<int:week>/', views.api_week_info, name='api_week_info'),
    path('api/mark-message-read/<uuid:message_id>/', views.api_mark_message_read, name='api_mark_message_read'),
    
    # Appointment management
    path('appointments/create/', views.create_appointment, name='create_appointment'),
    path('appointments/<uuid:appointment_id>/update/', views.update_appointment, name='update_appointment'),
    path('appointments/<uuid:appointment_id>/cancel/', views.cancel_appointment, name='cancel_appointment'),
    
    # Message management
    path('messages/conversation/<uuid:user_id>/', views.conversation, name='conversation'),
    path('messages/send/', views.send_message, name='send_message'),
]
