"""Common views for Apatye project."""
from django.conf import settings
from django.core.cache import cache
from django.db import connection
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Return the health status of the application and its dependencies."""

    health_status = {
        'status': 'healthy',
        'city': settings.CITY_NAME,
        'timezone': settings.TIME_ZONE,
        'language': settings.LANGUAGE_CODE,
    }
    status_code = status.HTTP_200_OK

    try:
        connection.ensure_connection()
        health_status['database'] = 'connected'
    except Exception as exc:  # pragma: no cover - defensive
        health_status['database'] = f'error: {exc}'
        health_status['status'] = 'unhealthy'
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    try:
        cache.set('health_check', 'ok', 10)
        if cache.get('health_check') == 'ok':
            health_status['redis'] = 'connected'
        else:
            health_status['redis'] = 'error'
            if health_status.get('status') != 'unhealthy':
                health_status['status'] = 'degraded'
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    except Exception as exc:  # pragma: no cover - defensive
        health_status['redis'] = f'error: {exc}'
        if health_status.get('status') != 'unhealthy':
            health_status['status'] = 'degraded'
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return Response(health_status, status=status_code)
