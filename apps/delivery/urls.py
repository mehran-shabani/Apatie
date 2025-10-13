"""URL patterns for delivery APIs."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import DeliveryOrderViewSet

router = DefaultRouter()
router.register(r'', DeliveryOrderViewSet, basename='delivery-order')

urlpatterns = [
    path('', include(router.urls)),
]
