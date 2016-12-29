"""
Test settings for trampoline.
"""

DEBUG = True

DATABASES = {
    'default': {
        'NAME': 'trampoline.db',
        'ENGINE': 'django.db.backends.sqlite3',
        'TEST': {
            'NAME': 'trampoline.db',
        },
        'TEST_NAME': 'trampoline.db',
    }
}

INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'trampoline',
    'tests',
)

LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'trampoline.tasks': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    }
}

SECRET_KEY = 'secret-key'

##################################################
#                   Trampoline                   #
##################################################

TRAMPOLINE = {
    'MODELS': [
        'tests.models.Token',
    ],
    'OPTIONS': {
        'disabled': False,
        'fail_silently': True,
    },
    'VERSION_SUFFIX': '_1',
}

##################################################
#                     Celery                     #
##################################################

CELERY_ALWAYS_EAGER = True
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True

from . import celery_app  # noqa
