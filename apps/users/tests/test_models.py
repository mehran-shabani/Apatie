"""Model tests for the users app."""
from datetime import timedelta

import pytest
from django.utils import timezone

from apps.users.models import OTPCode, User


@pytest.mark.django_db
def test_user_full_name_and_str(user_factory):
    """Full name should fallback to mobile when missing."""

    user = user_factory(first_name='Ali', last_name='Rezaei')
    assert str(user) == user.mobile
    assert user.get_full_name() == 'Ali Rezaei'


@pytest.mark.django_db
def test_otp_code_validity(user_factory):
    """OTP should be valid until used or expired."""

    otp = OTPCode.objects.create(
        mobile=user_factory().mobile,
        code='123456',
        expires_at=timezone.now() + timedelta(minutes=5),
    )
    assert otp.is_valid() is True
    otp.is_used = True
    otp.save(update_fields=['is_used'])
    assert otp.is_valid() is False


@pytest.mark.django_db
def test_user_manager_create_superuser():
    """Creating a superuser should set privilege flags."""

    user = User.objects.create_superuser(mobile='09123456789', password='test-password')
    assert user.is_staff is True
    assert user.is_superuser is True
    assert user.is_active is True
