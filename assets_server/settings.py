"""
Django settings for assets_server project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Keep it secret, keep it safe!
# (Although it's probably irrelevent to this app)
SECRET_KEY = 'a6f@ev$$r^@d4boc-gx^j3l@a=fr4rc^qq3my27zh)pn09$583'

ALLOWED_HOSTS = [
    '0.0.0.0', '127.0.0.1', 'localhost',
    '*.ubuntu.qa', '*.ubuntu.com', 'ubuntu.com'
]

INSTALLED_APPS = ['rest_framework']

MIDDLEWARE_CLASSES = []

ROOT_URLCONF = 'assets_server.urls'

WSGI_APPLICATION = 'assets_server.wsgi.application'

LANGUAGE_CODE = 'en-uk'
TIME_ZONE = 'UTC'
USE_I18N = False
USE_L10N = False
USE_TZ = False

REST_FRAMEWORK = {
    # Default format is JSON
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),

    # No complex permissions
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny'
    ]
}

# Mongo connection
# ===
from pymongo import MongoClient

from mappers import TokenManager

MONGO = MongoClient(os.environ.get('DATABASE_URL', 'mongodb://localhost/'))
TOKEN_MANAGER = TokenManager(data_collection=MONGO["assets"]["tokens"])
