"""
User views.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from .models import User
from .serializers import UserSerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for user management.
    """
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    
    @extend_schema(
        summary="Get current user profile",
        description="Returns the authenticated user's profile information."
    )
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user profile."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
