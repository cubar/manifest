from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'ja2a8kjbpd*x&ffh9awd9+vc(sk$1%$%wd&br2e%u8wsfons4s'

ALLOWED_HOSTS = ['*']

INSTALLED_APPS += ['django_sass',]

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

WAGTAIL_CACHE = False

try:
    from .local_settings import *
except ImportError:
    pass
