"""ViewSets for appointments."""
from rest_framework import permissions, viewsets

from .models import Appointment
from .serializers import AppointmentSerializer


class AppointmentViewSet(viewsets.ModelViewSet):
    """Manage appointment lifecycle."""

    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Appointment.objects.select_related('customer', 'vendor', 'vendor__user')
        if user.is_staff or user.is_superuser:
            return queryset
        if hasattr(user, 'vendor_profile'):
            return queryset.filter(vendor=user.vendor_profile)
        return queryset.filter(customer=user)

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)
