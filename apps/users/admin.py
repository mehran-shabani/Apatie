"""
User admin configurations.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, OTPCode


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin for custom User model."""
    list_display = ('mobile', 'email', 'first_name', 'last_name', 'user_type', 'is_verified', 'is_active', 'created_at')
    list_filter = ('user_type', 'is_verified', 'is_active', 'is_staff', 'created_at')
    search_fields = ('mobile', 'email', 'first_name', 'last_name')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('mobile', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('User type'), {'fields': ('user_type',)}),
        (_('Permissions'), {'fields': ('is_active', 'is_verified', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('mobile', 'password1', 'password2', 'user_type', 'is_active', 'is_verified'),
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'last_login')


@admin.register(OTPCode)
class OTPCodeAdmin(admin.ModelAdmin):
    """Admin for OTP codes."""
    list_display = ('mobile', 'code', 'is_used', 'expires_at', 'created_at')
    list_filter = ('is_used', 'created_at')
    search_fields = ('mobile', 'code')
    readonly_fields = ('created_at', 'updated_at')
