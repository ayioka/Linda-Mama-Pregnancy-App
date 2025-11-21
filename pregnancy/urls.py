from django.urls import path
from . import views

urlpatterns = [
# Authentication URLs
path('', views.home, name='home'),
path('login/', views.custom_login, name='login'),
path('logout/', views.custom_logout, name='logout'),
path('register/', views.signup, name='register'),
path('activate/<uidb64>/<token>/', views.activate, name='activate'),

```
# Role-based Dashboard URLs
path('dashboard/', views.patient_dashboard, name='patient_dashboard'),
path('clinician/dashboard/', views.clinician_dashboard, name='clinician_dashboard'),
path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),

# Profile URLs
path('profile/', views.profile_view, name='profile'),

# Appointment URLs
path('appointments/', views.appointments_list, name='appointments_list'),
path('appointments/create/', views.appointment_create, name='appointment_create'),
path('appointments/<int:appointment_id>/edit/', views.appointment_edit, name='appointment_edit'),
path('appointments/<int:appointment_id>/delete/', views.appointment_delete, name='appointment_delete'),

# Health Metrics URLs
path('health-metrics/', views.health_metrics_list, name='health_metrics_list'),
path('health-metrics/create/', views.health_metric_create, name='health_metric_create'),
path('health-metrics/<int:metric_id>/edit/', views.health_metric_edit, name='health_metric_edit'),

# Pregnancy Milestones URLs
path('pregnancy-milestones/', views.pregnancy_milestones, name='pregnancy_milestones'),
path('pregnancy-milestones/week/<int:week>/', views.milestone_detail, name='milestone_detail'),

# Clinician-specific URLs
path('clinician/patients/', views.clinician_patients, name='clinician_patients'),
path('clinician/patients/<int:patient_id>/', views.clinician_patient_detail, name='clinician_patient_detail'),
```

]

# Custom error handlers

handler404 = 'pregnancy.views.handler404'
handler500 = 'pregnancy.views.handler500'
