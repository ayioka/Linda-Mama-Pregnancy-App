from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Public pages
    path('', views.home, name='home'),
    
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
    
    # Dashboard and main features
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('track-progress/', views.track_progress, name='track_progress'),
    path('log-vitals/', views.log_vitals, name='log_vitals'),
    path('appointments/', views.appointments, name='appointments'),
    path('emergency-alert/', views.emergency_alert, name='emergency_alert'),
    
    # Appointment management
    path('appointments/create/', views.create_appointment, name='create_appointment'),
    path('appointments/<uuid:appointment_id>/', views.appointment_detail, name='appointment_detail'),
    path('appointments/<uuid:appointment_id>/update/', views.update_appointment, name='update_appointment'),
    path('appointments/<uuid:appointment_id>/cancel/', views.cancel_appointment, name='cancel_appointment'),
    path('appointments/<uuid:appointment_id>/confirm/', views.confirm_appointment, name='confirm_appointment'),
    
    # Vitals management
    path('vitals/', views.vitals_list, name='vitals_list'),
    path('vitals/<uuid:vitals_id>/', views.vitals_detail, name='vitals_detail'),
    path('vitals/<uuid:vitals_id>/delete/', views.delete_vitals, name='delete_vitals'),
    
    # Pregnancy profile
    path('pregnancy-profile/create/', views.create_pregnancy_profile, name='create_pregnancy_profile'),
    path('pregnancy-profile/update/', views.update_pregnancy_profile, name='update_pregnancy_profile'),
    
    # Error handlers
    path('404/', views.handler404, name='404'),
    path('500/', views.handler500, name='500'),
]
