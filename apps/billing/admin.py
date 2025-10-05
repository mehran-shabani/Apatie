"""
Billing admin configurations.
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from apps.common.admin import TimeStampedAdmin

from .models import Subscription, PaymentTransaction


@admin.register(Subscription)
class SubscriptionAdmin(TimeStampedAdmin):
    """Admin for Subscription model."""
    list_display = (
        'id', 'user', 'vendor', 'plan_type', 'status',
        'amount_paid', 'duration_months', 'starts_at', 'expires_at', 'created_at'
    )
    list_filter = ('status', 'plan_type', 'created_at')
    search_fields = ('user__mobile', 'vendor__name', 'notes')
    readonly_fields = ('created_at', 'updated_at', 'payment_transaction')
    raw_id_fields = ('user', 'vendor')
    
    fieldsets = (
        (None, {
            'fields': ('user', 'vendor', 'plan_type', 'status')
        }),
        (_('Payment Info'), {
            'fields': ('amount_paid', 'duration_months', 'payment_transaction')
        }),
        (_('Dates'), {
            'fields': ('starts_at', 'expires_at', 'created_at', 'updated_at')
        }),
        (_('Additional Info'), {
            'fields': ('notes',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'vendor', 'payment_transaction')


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(TimeStampedAdmin):
    """Admin for PaymentTransaction model."""
    list_display = (
        'order_id', 'user', 'gateway', 'purpose', 'amount_irr',
        'status', 'track_id', 'paid_at', 'created_at'
    )
    list_filter = ('gateway', 'status', 'purpose', 'created_at')
    search_fields = ('order_id', 'track_id', 'user__mobile', 'ref_number', 'card_pan_masked')
    readonly_fields = (
        'created_at', 'updated_at', 'track_id', 'paid_at',
        'result_code', 'message', 'card_pan_masked', 'ref_number'
    )
    raw_id_fields = ('user', 'vendor')
    
    fieldsets = (
        (None, {
            'fields': ('user', 'vendor', 'purpose', 'amount_irr')
        }),
        (_('Gateway Info'), {
            'fields': ('gateway', 'order_id', 'track_id', 'status', 'callback_url')
        }),
        (_('Payment Result'), {
            'fields': ('result_code', 'message', 'paid_at', 'card_pan_masked', 'ref_number')
        }),
        (_('Metadata'), {
            'fields': ('meta',),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'vendor')
    
    def has_add_permission(self, request):
        """Disable manual addition - transactions created via API."""
        return False
