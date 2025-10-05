"""
URL configuration for Apatye project.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

from apps.common.views import health_check

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Health check
    path('health/', health_check, name='health-check'),
    
    # API Schema & Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # API endpoints
    path('api/users/', include('apps.users.urls')),
    path('api/vendors/', include('apps.vendors.urls')),
    path('api/services/', include('apps.services.urls')),
    path('api/appointments/', include('apps.appointments.urls')),
    path('api/delivery/', include('apps.delivery.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
    path('api/billing/', include('apps.billing.urls')),
]

# Admin site configuration
admin.site.site_header = 'Apatye Admin - آپاتیه'
admin.site.site_title = 'Apatye Admin'
admin.site.index_title = 'Welcome to Apatye Administration'

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Debug toolbar
    try:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass
