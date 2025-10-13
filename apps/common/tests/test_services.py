"""Service layer tests for common utilities."""
import pytest
from rest_framework.exceptions import ValidationError

from apps.common import exceptions


def test_get_user_message_for_validation_error():
    """Validation errors should return translated message."""

    exc = ValidationError({'field': ['invalid']})
    message = exceptions._get_user_message(exc)
    assert 'not valid' in message.lower()


@pytest.mark.django_db
def test_custom_exception_handler_formats_response():
    """Custom exception handler should wrap details payload."""

    exc = ValidationError({'field': ['invalid']})
    context = {'view': object(), 'request': None}
    response = exceptions.custom_exception_handler(exc, context)
    assert response.data['success'] is False
    assert response.data['error']['status_code'] == response.status_code
    assert response.data['error']['details'] == {'field': ['invalid']}
