"""Views for vendor management."""
from typing import ClassVar, List, Type

from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Vendor
from .serializers import VendorSerializer
from .services import verify_vendor, deactivate_vendor


class IsVendorOwnerOrStaff(permissions.BasePermission):
    """Allow unsafe operations to vendor owners or staff members."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return user.is_staff or user.is_superuser or hasattr(user, 'vendor_profile')


class VendorViewSet(viewsets.ModelViewSet):
    """CRUD operations for vendors."""

    serializer_class = VendorSerializer
    permission_classes: ClassVar[List[Type[permissions.BasePermission]]] = [
        permissions.IsAuthenticated,
        IsVendorOwnerOrStaff,
    ]

    def get_queryset(self):
        user = self.request.user
        queryset = Vendor.objects.select_related('user')
        if user.is_staff or user.is_superuser:
            return queryset
        if hasattr(user, 'vendor_profile'):
            return queryset.filter(pk=user.vendor_profile_id)
        return queryset.filter(is_active=True, is_verified=True)

    def _assert_can_mutate(self, vendor):
        """Ensure that only staff or the owning vendor can mutate vendor records."""

        user = self.request.user

        if user.is_staff or user.is_superuser:
            return

        if hasattr(user, 'vendor_profile') and vendor.pk == user.vendor_profile_id:
            return

        raise PermissionDenied('Only the vendor owner or staff can modify vendor records.')

    def perform_update(self, serializer):
        vendor = self.get_object()
        self._assert_can_mutate(vendor)

        if hasattr(self.request.user, 'vendor_profile') and vendor.user == self.request.user:
            serializer.save(user=vendor.user)
        else:
            serializer.save()

    def perform_destroy(self, instance):
        self._assert_can_mutate(instance)
        instance.delete()

    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Mark a vendor as verified (staff only)."""

        vendor = self.get_object()
        if not (request.user.is_staff or request.user.is_superuser):
            return Response({'detail': 'Permission denied.'}, status=403)
        verify_vendor(vendor)
        serializer = self.get_serializer(vendor)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a vendor (staff or the vendor themselves)."""

        vendor = self.get_object()
        user = request.user
        if not (user.is_staff or user.is_superuser or vendor.user == user):
            return Response({'detail': 'Permission denied.'}, status=403)
        deactivate_vendor(vendor)
        serializer = self.get_serializer(vendor)
        return Response(serializer.data)
