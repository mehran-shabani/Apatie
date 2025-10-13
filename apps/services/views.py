"""ViewSets for managing services."""
from typing import ClassVar, List, Type

from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied

from .models import Service
from .serializers import ServiceSerializer


class IsVendorOrStaffOrReadOnly(permissions.BasePermission):
    """Allow unsafe operations only to staff or vendors."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return user.is_staff or user.is_superuser or hasattr(user, 'vendor_profile')


class ServiceViewSet(viewsets.ModelViewSet):
    """API endpoint for listing and managing services."""

    serializer_class = ServiceSerializer
    permission_classes: ClassVar[List[Type[permissions.BasePermission]]] = [
        permissions.IsAuthenticated,
        IsVendorOrStaffOrReadOnly,
    ]

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

        if vendor is None:
            raise PermissionDenied('Staff must specify a vendor when creating services.')

        serializer.save()

    def _assert_can_mutate(self, instance):
        """Ensure only staff or the owning vendor can mutate a service."""

        user = self.request.user

        if user.is_staff or user.is_superuser:
            return

        if hasattr(user, 'vendor_profile') and instance.vendor == user.vendor_profile:
            return

        raise PermissionDenied('Only the owning vendor or staff can modify services.')

    def perform_update(self, serializer):
        """Apply ownership rules on update operations."""

        instance = self.get_object()
        self._assert_can_mutate(instance)

        if hasattr(self.request.user, 'vendor_profile'):
            serializer.save(vendor=instance.vendor)
        else:
            serializer.save()

    def perform_destroy(self, instance):
        """Apply ownership rules on delete operations."""

        self._assert_can_mutate(instance)
        instance.delete()
