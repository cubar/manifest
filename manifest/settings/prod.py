from .base import *  # noqa

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

SECRET_KEY = env('SECRET_KEY')  # noqa

# Add your site's domain name(s) here.
ALLOWED_HOSTS = ['manifest.ncpn.nl']

# To send email from the server, we recommend django_sendmail_backend
# Or specify your own email backend such as an SMTP server.
# https://docs.djangoproject.com/en/3.2/ref/settings/#email-backend
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.ncpn.nl'
EMAIL_HOST_USER = 'manifest@ncpn.nl'
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')  # noqa
EMAIL_POST = 587
EMAIL_USE_TLS = True

# Default email address used to send messages from the website.
DEFAULT_FROM_EMAIL = '\"Manifest, krant van de NCPN\" <manifest@ncpn.nl>'

# A list of people who get error notifications.
ADMINS = [
    ('Administrator', 'webdev@ncpn.nl'),
]

# A list in the same format as ADMINS that specifies who should get broken link
# (404) notifications when BrokenLinkEmailsMiddleware is enabled.
MANAGERS = ADMINS

# Email address used to send error messages to ADMINS.
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# Use template caching to speed up wagtail admin and front-end.
# Requires reloading web server to pick up template changes.
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'wagtail.contrib.settings.context_processors.settings',
            ],
            'loaders': [
                ('django.template.loaders.cached.Loader', [
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                ]),
            ],
        },
    },
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'manifestdb',
        'USER': 'manifest',
    },
}

WAGTAILSEARCH_BACKENDS = {
    "default": {
        "BACKEND": "wagtail.search.backends.database",
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': os.path.join(BASE_DIR, 'cache'),  # noqa
        'KEY_PREFIX': 'coderedcms',
        'TIMEOUT': 14400, # in seconds
    }
}

# Compression
#STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
#STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"
STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

# Storage
MEDIA_URL = "https://%s/" % AWS_S3_CUSTOM_DOMAIN  # noqa
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_S3_FILE_OVERWRITE = False
