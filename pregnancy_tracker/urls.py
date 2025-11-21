from django.contrib import admin
from django.urls import path, include
from pregnancy import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    
    # Authentication URLs
    path('login/', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('signup/', views.signup, name='signup'),
    
    # Profile & Dashboard URLs
    path('profile/', views.profile_view, name='profile'),  # updated
    path('dashboard/', views.patient_dashboard, name='dashboard'),  # updated
    
    # Pregnancy app URLs
    path('pregnancy/', include('pregnancy.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
