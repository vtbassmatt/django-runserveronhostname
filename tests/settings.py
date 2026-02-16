"""
Django settings for testing runserveronhostname package.
"""

SECRET_KEY = 'test-secret-key-for-testing-only'

DEBUG = True

INSTALLED_APPS = [
    'runserveronhostname',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

USE_TZ = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
}
