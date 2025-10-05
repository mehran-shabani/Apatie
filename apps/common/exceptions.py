"""Custom exception handling utilities for the project."""
import logging
from typing import Any

from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext as _
from rest_framework import status
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def _get_user_message(exc: Exception) -> str:
    """Return a user-friendly error message for the given exception."""

    if isinstance(exc, ValidationError):
        return _('Submitted data is not valid.')
    if isinstance(exc, PermissionDenied):
        return _('You do not have permission to perform this action.')
    if isinstance(exc, APIException) and getattr(exc, 'default_detail', None):
        try:
            return str(exc.default_detail)
        except Exception:  # pragma: no cover - defensive
            pass
    return str(exc)


def _serialise_details(detail: Any) -> Any:
    """Normalise the detail payload into JSON-safe structures."""

    if isinstance(detail, (list, dict)):
        return detail
    if detail:
        return [detail]
    return None


def custom_exception_handler(exc, context):
    """Custom exception handler that provides consistent error responses."""

    response = exception_handler(exc, context)

    if response is not None:
        custom_response_data = {
            'success': False,
            'error': {
                'message': _get_user_message(exc),
                'status_code': response.status_code,
            },
        }

        if hasattr(exc, 'detail'):
            serialised_detail = _serialise_details(exc.detail)
            if serialised_detail is not None:
                custom_response_data['error']['details'] = serialised_detail

        response.data = custom_response_data
        return response

    logger.error('Unhandled exception: %s', exc, exc_info=True)
    custom_response_data = {
        'success': False,
        'error': {
            'message': _('An unexpected error occurred.'),
            'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR,
        },
    }
    return Response(custom_response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
