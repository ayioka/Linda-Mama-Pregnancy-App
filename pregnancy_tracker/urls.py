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
    
    # Activation URL
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    
    # Pregnancy app URLs - this will include all other URLs
    path('', include('pregnancy.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
