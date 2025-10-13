"""Test settings for Apatye project."""
from .base import *  # noqa

DATABASES = {
    'default': env.db('TEST_DATABASE_URL', default='sqlite:///test.sqlite3'),
}

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

MIGRATION_MODULES = {
    'billing': None,
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
