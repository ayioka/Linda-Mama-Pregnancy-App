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
    path('login/', auth_views.LoginView.as_view(template_name='pregnancy/auth/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),

    # Password reset
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='pregnancy/auth/password_reset.html',
             email_template_name='pregnancy/auth/password_reset_email.html',
             subject_template_name='pregnancy/auth/password_reset_subject.txt'
         ),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='pregnancy/auth/password_reset_done.html'),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='pregnancy/auth/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='pregnancy/auth/password_reset_complete.html'),
         name='password_reset_complete'),

    # Dashboard and profile
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('profile/update-pregnancy/', views.update_pregnancy_profile, name='update_pregnancy_profile'),

    # Pregnancy features
    path('track-progress/', views.track_progress, name='track_progress'),
    path('log-vitals/', views.log_vitals, name='log_vitals'),
    path('educational-content/', views.educational_content, name='educational_content'),
    path('educational-content/<slug:slug>/', views.content_detail, name='content_detail'),

    # Appointments
    path('appointments/', views.appointments, name='appointments'),
    path('appointments/create/', views.create_appointment, name='create_appointment'),

    # Messaging
    path('messaging/', views.messaging, name='messaging'),
    path('messages/conversation/<uuid:user_id>/', views.conversation, name='conversation'),

    # Emergency alert
    path('emergency-alert/', views.emergency_alert, name='emergency_alert'),

    # API endpoints
    path('api/week-info/<int:week>/', views.api_week_info, name='api_week_info'),
    path('api/mark-message-read/<uuid:message_id>/', views.api_mark_message_read, name='api_mark_message_read'),
]
