"""
WSGI config for manifest project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os
import environ

from django.core.wsgi import get_wsgi_application

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(PROJECT_DIR)

env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "manifest.settings.%s" % (env('ENV_VALUE')) )

application = get_wsgi_application()

