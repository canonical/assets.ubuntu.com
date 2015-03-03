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
from swiftclient.client import Connection as SwiftConnection

# Local
from mappers import DataManager, FileManager, TokenManager
from lib.db_helpers import mongo_db_from_url

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Keep it secret, keep it safe!
# (Although it's probably irrelevent to this app)
SECRET_KEY = 'a6f@ev$$r^@d4boc-gx^j3l@a=fr4rc^qq3my27zh)pn09$583'

ALLOWED_HOSTS = ['*']

DEBUG = os.environ.get('WSGI_DEBUG', "").lower() == 'true'

INSTALLED_APPS = ['rest_framework']

MIDDLEWARE_CLASSES = []

ROOT_URLCONF = 'assets_server.urls'

WSGI_APPLICATION = 'assets_server.wsgi.application'

LANGUAGE_CODE = 'en-uk'
TIME_ZONE = 'UTC'
USE_I18N = False
USE_L10N = False
USE_TZ = False

DEFAULT_JSON_INDENT = 4

REST_FRAMEWORK = {
    # Default format is JSON
    'DEFAULT_RENDERER_CLASSES': (
        'assets_server.renderers.PrettyJSONRenderer',
    ),

    # No complex permissions
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny'
    ]
}

MONGO_DB = mongo_db_from_url(
    mongo_url=os.environ.get('MONGO_URL'),
    default_database='assets'
)

TOKEN_MANAGER = TokenManager(data_collection=MONGO_DB['tokens'])
DATA_MANAGER = DataManager(data_collection=MONGO_DB['asset_data'])
FILE_MANAGER = FileManager(
    SwiftConnection(
        os.environ.get('OS_AUTH_URL'),
        os.environ.get('OS_USERNAME'),
        os.environ.get('OS_PASSWORD'),
        auth_version='2.0',
        os_options={'tenant_name': os.environ.get('OS_TENANT_NAME')}
    )
)


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
