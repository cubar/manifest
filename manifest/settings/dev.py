from .base import *  # noqa

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

SECRET_KEY = 'dev'

INSTALLED_APPS += ['django_sass',]  # noqa

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

WAGTAIL_CACHE = False
