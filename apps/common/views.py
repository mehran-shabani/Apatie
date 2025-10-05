"""
Common views for Apatye project.
"""
from django.conf import settings
from django.db import connection
from django.http import JsonResponse
from rest_framework import status


def health_check(request):
    """
    Health check endpoint.
    Returns 200 if the application is healthy.
    """
    health_status = {
        'status': 'healthy',
        'city': settings.CITY_NAME,
        'timezone': settings.TIME_ZONE,
        'language': settings.LANGUAGE_CODE,
    }
    
    # Check database connection
    try:
        connection.ensure_connection()
        health_status['database'] = 'connected'
    except Exception as e:
        health_status['database'] = f'error: {str(e)}'
        return JsonResponse(health_status, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    
    # Check Redis connection
    try:
        from django.core.cache import cache
        cache.set('health_check', 'ok', 10)
        if cache.get('health_check') == 'ok':
            health_status['redis'] = 'connected'
        else:
            health_status['redis'] = 'error'
    except Exception as e:
        health_status['redis'] = f'error: {str(e)}'
    
    return JsonResponse(health_status, status=status.HTTP_200_OK)
