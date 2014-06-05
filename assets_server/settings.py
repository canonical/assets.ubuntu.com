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


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'a6f@ev$$r^@d4boc-gx^j3l@a=fr4rc^qq3my27zh)pn09$583'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = (
    'rest_framework',
    'django_extensions'
)

MIDDLEWARE_CLASSES = ()

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
