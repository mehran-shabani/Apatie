"""Service layer tests for user helpers."""
import pytest

from apps.users.models import User


@pytest.mark.django_db
def test_create_user_requires_mobile():
    """User manager should validate presence of mobile."""

    with pytest.raises(ValueError):
        User.objects.create_user(mobile='', password='secret')


@pytest.mark.django_db
def test_create_user_hashes_password():
    """Passwords should be stored as hashes."""

    user = User.objects.create_user(mobile='09100000000', password='plain-pass')
    assert user.check_password('plain-pass') is True
