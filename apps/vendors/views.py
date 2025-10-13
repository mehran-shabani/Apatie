"""Views for vendor management."""
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Vendor
from .serializers import VendorSerializer
from .services import verify_vendor, deactivate_vendor


class VendorViewSet(viewsets.ModelViewSet):
    """CRUD operations for vendors."""

    serializer_class = VendorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Vendor.objects.select_related('user')
        if user.is_staff or user.is_superuser:
            return queryset
        if hasattr(user, 'vendor_profile'):
            return queryset.filter(pk=user.vendor_profile_id)
        return queryset.filter(is_active=True, is_verified=True)

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
