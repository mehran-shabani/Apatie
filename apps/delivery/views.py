"""Delivery order API views."""
from rest_framework import permissions, viewsets

from .models import DeliveryOrder
from .serializers import DeliveryOrderSerializer


class DeliveryOrderViewSet(viewsets.ReadOnlyModelViewSet):
    """Expose delivery orders to customers and vendors."""

    serializer_class = DeliveryOrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = DeliveryOrder.objects.select_related('appointment', 'appointment__customer', 'appointment__vendor')
        if user.is_staff or user.is_superuser:
            return queryset
        if hasattr(user, 'vendor_profile'):
            return queryset.filter(appointment__vendor=user.vendor_profile)
        return queryset.filter(appointment__customer=user)
