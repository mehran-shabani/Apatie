"""
Custom exception handler for Apatye project.
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides consistent error responses.
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    if response is not None:
        # Customize the response data
        custom_response_data = {
            'success': False,
            'error': {
                'message': str(exc),
                'status_code': response.status_code,
            }
        }
        
        # Add detail if available
        if hasattr(exc, 'detail'):
            custom_response_data['error']['details'] = exc.detail
        
        response.data = custom_response_data
    else:
        # Handle unexpected exceptions
        logger.error(f'Unhandled exception: {exc}', exc_info=True)
        custom_response_data = {
            'success': False,
            'error': {
                'message': 'An unexpected error occurred.',
                'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR,
            }
        }
        response = Response(custom_response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return response
