"""
Django settings for assets_server project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# System
import os

# Modules
import swiftclient

# Local
from .mappers import DataManager, FileManager, TokenManager, RedirectManager
from .lib.db_helpers import mongo_db_from_url

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SECRET_KEY = os.environ.get('SECRET_KEY', 'no_secret')

ALLOWED_HOSTS = ['*']

DEBUG = os.environ.get('DJANGO_DEBUG', 'false').lower() == 'true'

INSTALLED_APPS = [
    'rest_framework',
    'webapp'
]

MIDDLEWARE_CLASSES = []

ROOT_URLCONF = 'webapp.urls'
WSGI_APPLICATION = 'webapp.wsgi.application'

LANGUAGE_CODE = 'en-uk'
TIME_ZONE = 'UTC'
USE_I18N = False
USE_L10N = False
USE_TZ = False

DEFAULT_JSON_INDENT = 4

REST_FRAMEWORK = {
    # Default format is JSON
    'DEFAULT_RENDERER_CLASSES': (
        'webapp.renderers.PrettyJSONRenderer',
    ),

    # No complex permissions
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny'
    ],

    # Disable authentication
    'UNAUTHENTICATED_USER': None
}

MONGO_DB = mongo_db_from_url(
    mongo_url=os.environ.get('MONGO_URL', 'db'),
    default_database='assets'
)

TOKEN_MANAGER = TokenManager(data_collection=MONGO_DB['tokens'])
REDIRECT_MANAGER = RedirectManager(data_collection=MONGO_DB['redirects'])
DATA_MANAGER = DataManager(data_collection=MONGO_DB['asset_data'])

SWIFT_CONNECTION = swiftclient.client.Connection(
    'http://swift:8080/auth/v1.0',
    'test:tester',
    'testing',
    auth_version='1.0'
)

swift_settings = [
    'OS_AUTH_URL', 'OS_USERNAME', 'OS_PASSWORD', 'OS_TENANT_NAME'
]
if set(swift_settings).issubset(set(os.environ)):
    SWIFT_CONNECTION = swiftclient.client.Connection(
        os.environ.get('OS_AUTH_URL'),
        os.environ.get('OS_USERNAME'),
        os.environ.get('OS_PASSWORD'),
        auth_version='2.0',
        os_options={'tenant_name': os.environ.get('OS_TENANT_NAME')}
    )

FILE_MANAGER = FileManager(SWIFT_CONNECTION)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'error_file': {
            'level': 'ERROR',
            'filename': os.path.join(BASE_DIR, 'django-error.log'),
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 1 * 1024 * 1024,
            'backupCount': 2
        }
    },
    'loggers': {
        'django': {
            'handlers': ['error_file'],
            'level': 'ERROR',
            'propagate': True
        }
    }
}
