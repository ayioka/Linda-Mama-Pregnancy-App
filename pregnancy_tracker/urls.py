from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from dashboard.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('dashboard/', include('dashboard.urls')),
    path('users/', include('users.urls')),
    path('pregnancy/', include('pregnancy.urls')),
    path('appointments/', include('appointments.urls')),
    path('messaging/', include('messaging.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
