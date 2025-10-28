from django.urls import path
from . import views

app_name = 'pregnancy'

urlpatterns = [
    path('create/', views.pregnancy_create, name='pregnancy_create'),
    path('<int:pk>/', views.pregnancy_detail, name='pregnancy_detail'),
    path('<int:pregnancy_pk>/health-metrics/', views.health_metrics_log, name='health_metrics_log'),
]
