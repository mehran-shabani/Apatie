"""URL patterns for vendor APIs."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import VendorViewSet

router = DefaultRouter()
router.register(r'', VendorViewSet, basename='vendor')

urlpatterns = [
    path('', include(router.urls)),
]
