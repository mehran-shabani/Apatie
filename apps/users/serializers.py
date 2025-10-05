"""
User serializers.
"""
from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    
    class Meta:
        model = User
        fields = ('id', 'mobile', 'email', 'first_name', 'last_name', 'user_type', 'is_verified', 'created_at')
        read_only_fields = ('id', 'user_type', 'is_verified', 'created_at')
