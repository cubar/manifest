"""
Django settings for manifest project.

Generated by 'django-admin startproject' using Django 3.2.12.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import environ
import os

# Set up environment variables


PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(PROJECT_DIR)

env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Application definition

INSTALLED_APPS = [
    # This project
    'website',
    'storages',

    # CodeRed CMS
    'coderedcms',
    'django_bootstrap5',
    'modelcluster',
    'taggit',
    'wagtailfontawesome',
    'wagtailcache',
    'wagtailseo',

    # Wagtail
    'wagtail.contrib.forms',
    'wagtail.contrib.redirects',
    'wagtail.embeds',
    'wagtail.sites',
    'wagtail.users',
    'wagtail.snippets',
    'wagtail.documents',
    'wagtail.images',
    'wagtail.search',
    'wagtail.core',
    'wagtail.contrib.settings',
    'wagtail.contrib.modeladmin',
    'wagtail.contrib.table_block',
    'wagtail.admin',

    # Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
]

MIDDLEWARE = [
    # Save pages to cache. Must be FIRST.
    'wagtailcache.cache.UpdateCacheMiddleware',

    # Common functionality
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.common.CommonMiddleware',

    # Security
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',

    'whitenoise.middleware.WhiteNoiseMiddleware', # to speed up static file serving

    # Error reporting. Uncomment this to receive emails when a 404 is triggered.
    #'django.middleware.common.BrokenLinkEmailsMiddleware',

    # CMS functionality
    'wagtail.contrib.redirects.middleware.RedirectMiddleware',

    # Fetch from cache. Must be LAST.
    'wagtailcache.cache.FetchFromCacheMiddleware',
]

ROOT_URLCONF = 'manifest.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'wagtail.contrib.settings.context_processors.settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'manifest.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'manifestdb',
            'USER': 'manifest'
        },
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

# LANGUAGE_CODE = 'nl'

# TIME_ZONE = 'Europe/Amsterdam'

# USE_I18N = False

# USE_L10N = True

# USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'


# Login

LOGIN_URL = 'wagtailadmin_login'
LOGIN_REDIRECT_URL = 'wagtailadmin_home'


# Wagtail settings

WAGTAIL_SITE_NAME = "Manifest, krant van de NCPN"

WAGTAIL_ENABLE_UPDATE_CHECK = False


# Base URL to use when referring to full URLs within the Wagtail admin backend -
# e.g. in notification emails. Don't include '/admin' or a trailing slash
WAGTAILADMIN_BASE_URL = 'http://manifest.ncpn.nl'

# Tags

TAGGIT_CASE_INSENSITIVE = True

AWS_STORAGE_BUCKET_NAME = 'images.manifest.ncpn.nl'
AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
AWS_S3_CUSTOM_DOMAIN = '%s/%s' % (AWS_STORAGE_BUCKET_NAME, AWS_STORAGE_BUCKET_NAME)
AWS_S3_ENDPOINT_URL = 'https://%s/' % AWS_STORAGE_BUCKET_NAME


# Sets default for primary key IDs
# See https://docs.djangoproject.com/en/3.2/ref/models/fields/#bigautofield
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

DATE_FORMAT = 'Y-m-d'
LANGUAGE_CODE = 'nl-nl'
TIME_ZONE = 'Europe/Amsterdam'
USE_I18N = True
USE_L10N = True
USE_TZ = False
# STATIC_URL = '/static/'
# STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)
X_FRAME_OPTIONS = 'DENY'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/var/log/manifest/debug.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
# overwriting...
LOGGING = {
  'version': 1,
  'loggers': {
      'asyncio': {
          'level': 'WARNING',
      },
  },
}

# It is necesary to add all of these blocks in a list if you want to add your own custom one as described in github issue: https://github.com/coderedcorp/coderedcms/issues/530
CRX_FRONTEND_TEMPLATES_BLOCKS = {
        "cardblock": [
            (
                "coderedcms/blocks/card_block.html",
                "Card",
            ),
            (
                "coderedcms/blocks/card_head.html",
                "Card with header",
            ),
            (
                "coderedcms/blocks/card_foot.html",
                "Card with footer",
            ),
            (
                "coderedcms/blocks/card_head_foot.html",
                "Card with header and footer",
            ),
            (
                "coderedcms/blocks/card_blurb.html",
                "Blurb - rounded image and no border",
            ),
            (
                "coderedcms/blocks/card_img.html",
                "Cover image - use image as background",
            ),
        ],
        "cardgridblock": [
            (
                "coderedcms/blocks/cardgrid_group.html",
                "Card group - attached cards of equal size",
            ),
            (
                "coderedcms/blocks/cardgrid_deck.html",
                "Card deck - separate cards of equal size",
            ),
            (
                "coderedcms/blocks/cardgrid_columns.html",
                "Card masonry - fluid brick pattern",
            ),
        ],
        "pagelistblock": [
            (
                "coderedcms/blocks/pagelist_block.html",
                "General, simple list",
            ),
            (
                "coderedcms/blocks/pagelist_list_group.html",
                "General, list group navigation panel",
            ),
            (
                "coderedcms/blocks/pagelist_article_media.html",
                "Article, media format",
            ),
            (
                "coderedcms/blocks/pagelist_article_card_group.html",
                "Article, card group - attached cards of equal size",
            ),
            (
                "coderedcms/blocks/pagelist_article_card_deck.html",
                "Article, card deck - separate cards of equal size",
            ),
            (
                "coderedcms/blocks/pagelist_article_card_columns.html",
                "Article, card masonry - fluid brick pattern",
            ),
            (
                "website/blocks/pagelist_headlines.html",
                "Headlines block for Manifest home page",
            ),
            (
                "website/blocks/pagelist_newsstream.html",
                "News stream block for Manifest home page",
            ),
            (
                "website/blocks/pagelist_frontpagetopic_left.html",
                "Specific topic block for Manifest home page",
            ),
        ],
        "pagepreviewblock": [
            (
                "coderedcms/blocks/pagepreview_card.html",
                "Card",
            ),
            (
                "coderedcms/blocks/pagepreview_form.html",
                "Form inputs",
            ),
        ],
        # templates that are available for all block types
        "*": [
            ("", "Default"),
        ],
    }

