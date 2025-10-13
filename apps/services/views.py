"""ViewSets for managing services."""
from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied

from .models import Service
from .serializers import ServiceSerializer


class ServiceViewSet(viewsets.ModelViewSet):
    """API endpoint for listing and managing services."""

    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Restrict services based on the requesting user's role."""

        queryset = Service.objects.select_related('vendor', 'vendor__user')
        user = self.request.user

        if user.is_superuser or user.is_staff:
            return queryset
        if hasattr(user, 'vendor_profile'):
            return queryset.filter(vendor=user.vendor_profile)
        return queryset.filter(is_active=True, vendor__is_active=True)

    def perform_create(self, serializer):
        """Ensure vendors can only create services for themselves."""

        user = self.request.user
        vendor = serializer.validated_data.get('vendor')

        if hasattr(user, 'vendor_profile'):
            if vendor and vendor != user.vendor_profile:
                raise PermissionDenied('You can only manage your own services.')
            serializer.save(vendor=user.vendor_profile)
            return

        if not (user.is_staff or user.is_superuser):
            raise PermissionDenied('Only vendors or staff can create services.')

        serializer.save()

    def perform_update(self, serializer):
        """Apply the same ownership rules on update."""

        instance = self.get_object()
        user = self.request.user

        if hasattr(user, 'vendor_profile') and instance.vendor != user.vendor_profile:
            raise PermissionDenied('You can only manage your own services.')

        serializer.save()
