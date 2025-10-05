"""
Billing URL patterns.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    SubscriptionViewSet,
    PaymentTransactionViewSet,
    PaymentCallbackView,
)

router = DefaultRouter()
router.register(r'subscriptions', SubscriptionViewSet, basename='subscription')
router.register(r'transactions', PaymentTransactionViewSet, basename='transaction')

urlpatterns = [
    # Payment callback (separate from router)
    path('payments/zibal/callback/', PaymentCallbackView.as_view(), name='zibal-callback'),
    
    # Router URLs
    path('', include(router.urls)),
]
