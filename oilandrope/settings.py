"""
Django settings for Oil & Rope project.

Generated by 'django-admin startproject' using Django 2.2.2.

For more information on this file, see
https://docs.djangoproject.com/en/stable/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/stable/ref/settings/
"""

import os
from distutils.util import strtobool as to_bool
from pathlib import Path

from django.contrib.messages import constants as message_constants
from django.utils.translation import gettext_noop

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/stable/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(to_bool(os.getenv('DEBUG', 'False')))

# https://docs.djangoproject.com/en/stable/ref/settings/#allowed-hosts

ALLOWED_HOSTS_ENVIRON = os.getenv('ALLOWED_HOSTS')
if ALLOWED_HOSTS_ENVIRON:
    ALLOWED_HOSTS = ALLOWED_HOSTS_ENVIRON.split(',')
else:
    ALLOWED_HOSTS = [
        '.oilandrope-project.com',
    ]

# Since we need all trusted origins to begin with scheme let's add them
# https://docs.djangoproject.com/en/stable/ref/settings/#csrf-trusted-origins

CSRF_TRUSTED_ORIGINS = [f'https://{host}' for host in ALLOWED_HOSTS]

# Cookie secure should be always True on production
# https://docs.djangoproject.com/en/stable/ref/settings/#csrf-cookie-secure

CSRF_COOKIE_SECURE = to_bool(os.getenv('CSRF_COOKIE_SECURE', 'True'))

# https://docs.djangoproject.com/en/stable/ref/settings/#csrf-cookie-domain

CSRF_COOKIE_DOMAIN = os.getenv('CSRF_COOKIE_DOMAIN', '.oilandrope-project.com')

# Defines Admins
# https://docs.djangoproject.com/en/stable/ref/settings/#admins

ADMINS = [
    ('LeCuay', 'suso.becerra98@gmail.com'),
    ('Daniel', 'danielpaz4c@gmail.com'),
]

# Defines Manager
# https://docs.djangoproject.com/en/stable/ref/settings/#managers

MANAGERS = ADMINS

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # The “sites” framework (https://docs.djangoproject.com/en/stable/ref/contrib/sites/)
    'django.contrib.sites',
    # DjangoAllAuth (https://django-allauth.readthedocs.io/)
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    # DjangoAllAuth for Google (https://django-allauth.readthedocs.io/en/latest/providers.html#google)
    'allauth.socialaccount.providers.google',
    # DjangoChannels (https://channels.readthedocs.io/en/latest/index.html)
    'channels',
    # CKEditor's RichText (https://django-ckeditor.readthedocs.io/en/latest/)
    'ckeditor',
    # Bootstrap5 template
    'crispy_bootstrap5',
    # Model-Bootstrap Forms (https://django-crispy-forms.readthedocs.io/)
    'crispy_forms',
    # Django CORS (https://github.com/adamchainz/django-cors-headers)
    'corsheaders',
    # django-filter (https://django-filter.readthedocs.io/)
    'django_filters',
    # django-prometheus (https://github.com/korfuri/django-prometheus#quickstart)
    'django_prometheus',
    # drf_spectacular (https://drf-spectacular.readthedocs.io/)
    'drf_spectacular',
    # DjangoMptt (https://django-mptt.readthedocs.io/)
    'mptt',
    # API RestFramework (https://www.django-rest-framework.org/)
    'rest_framework',
    # RestFramework Token (https://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication)
    'rest_framework.authtoken',
    # Source
    'core.apps.CoreConfig',
    # API
    'api.apps.ApiConfig',
    # Common
    'common.apps.CommonConfig',
    # Bot
    'bot.apps.BotConfig',
    # Registration System
    'registration.apps.RegistrationConfig',
    # Chat
    'chat.apps.ChatConfig',
    # Roleplay
    'roleplay.apps.RoleplayConfig',
    # O&R Email
    'oar_email.apps.OAREmailConfig',
]


MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_prometheus.middleware.PrometheusAfterMiddleware',
]

# Changing messages tags to Bootstrap
# (https://docs.djangoproject.com/en/stable/ref/settings/#message-tags)

MESSAGE_TAGS = {
    message_constants.DEBUG: 'debug',
    message_constants.INFO: 'info',
    message_constants.SUCCESS: 'success',
    message_constants.WARNING: 'warning',
    message_constants.ERROR: 'danger',
}

# SITE_ID = 1 is for declaring page ID
# (https://docs.djangoproject.com/en/stable/ref/contrib/sites/#enabling-the-sites-framework)

SITE_ID = 1

ROOT_URLCONF = 'oilandrope.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'oar_email/templates/',
            BASE_DIR / 'common/templates/errors/',
            BASE_DIR / 'registration/templates/allauth/',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'common.context_processors.utils.requests_utils',
                'core.context_processors.language',
                'core.context_processors.handy_settings',
            ],
            'debug': bool(to_bool(os.getenv('DEBUG_TEMPLATE', 'False'))),
        },
    },
]

WSGI_APPLICATION = 'oilandrope.wsgi.application'

# DjangoChannels ASGI Router
ASGI_APPLICATION = 'oilandrope.asgi.application'

# Channel Layers
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [
                (os.getenv('CHANNEL_LAYER_HOST'), 6379)
            ],
        },
    },
}

# Database
# https://docs.djangoproject.com/en/stable/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'TEST': {
            'NAME': 'test_{}'.format(os.getenv('DB_NAME'))
        },
    },
}

# Default primary key field type
# https://docs.djangoproject.com/en/stable/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Password validation
# https://docs.djangoproject.com/en/stable/ref/settings/#auth-password-validators

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

# Model to use for User
# https://docs.djangoproject.com/en/stable/ref/settings/#auth-user-model

AUTH_USER_MODEL = 'registration.User'

# Authentication systems
# https://docs.djangoproject.com/en/stable/ref/settings/#authentication-backends

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'registration.backends.EmailBackend',
    # `allauth` authentication by specific allowed methods
    # https://django-allauth.readthedocs.io/en/latest/overview.html
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Internationalization
# https://docs.djangoproject.com/en/stable/topics/i18n/

LANGUAGE_CODE = 'en'

# Supported languages
# https://docs.djangoproject.com/en/stable/ref/settings/#languages
# NOTE: We use `gettext_noop` since it was is being used in `django.conf.global_settings`

LANGUAGES = [
    ('en', gettext_noop('English')),
    ('es', gettext_noop('Spanish')),
]

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Translation files

LOCALE_PATHS = [
    BASE_DIR / 'locale/',
]

# Session expire date
# https://docs.djangoproject.com/en/stable/ref/settings/#session-cookie-age

SESSION_COOKIE_AGE = 172800

# Cookie for Session shouldn't be accessible from JavaScript
# https://docs.djangoproject.com/en/stable/ref/settings/#session-cookie-httponly

SESSION_COOKIE_HTTPONLY = True

# https://docs.djangoproject.com/en/stable/ref/settings/#session-cookie-samesite

SESSION_COOKIE_SAMESITE = 'Lax'

# Cookie for session should be always secure on production
# https://docs.djangoproject.com/en/stable/ref/settings/#session-cookie-secure

SESSION_COOKIE_SECURE = to_bool(os.getenv('SESSION_COOKIE_SECURE', 'True'))

# https://docs.djangoproject.com/en/stable/ref/settings/#session-cookie-domain

SESSION_COOKIE_DOMAIN = os.getenv('SESSION_COOKIE_DOMAIN', '.oilandrope-project.com')

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/stable/howto/static-files/

STATIC_ROOT = os.getenv('STATIC_ROOT', BASE_DIR / 'static/')
STATIC_URL = os.getenv('STATIC_URL', '/static/')

# Since Oil & Rope uses custom styles, JavaScript and more we need to declare them

CUSTOMS_STATIC_URL = os.getenv('CUSTOMS_STATIC_URL', 'https://cdn.oilandrope-project.com/')

# Login System
# https://docs.djangoproject.com/en/stable/ref/settings/#auth

LOGIN_URL = 'registration:auth:login'
LOGIN_REDIRECT_URL = 'core:index'
LOGOUT_REDIRECT_URL = 'registration:auth:login'

# Media files
# https://docs.djangoproject.com/en/stable/ref/settings/#media-root

MEDIA_ROOT = os.getenv('MEDIA_ROOT', BASE_DIR / 'media/')
MEDIA_URL = os.getenv('MEDIA_URL', '/media/')

# The maximum size (in bytes)
# https://docs.djangoproject.com/en/stable/ref/settings/#file-upload-max-memory-size

FILE_UPLOAD_MAX_MEMORY_SIZE = 6291456

# The maximum size in bytes that a request body may be
# https://docs.djangoproject.com/en/stable/ref/settings/#data-upload-max-memory-size

DATA_UPLOAD_MAX_MEMORY_SIZE = FILE_UPLOAD_MAX_MEMORY_SIZE

# Using Pytest as test runner
# https://pytest-django.readthedocs.io/en/latest/faq.html#how-can-i-use-manage-py-test-with-pytest-django

TEST_RUNNER = 'oilandrope.runner.PytestTestRunner'

# CKEditor
# https://django-ckeditor.readthedocs.io/en/latest/#optional-customizing-ckeditor-editor

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Bold', 'Italic', 'Underline'],
            ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-',
             'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
            ['Link', 'Unlink'],
            ['RemoveFormat'],
        ],
        'uiColor': '#EE7A55',
        'resize_enabled': False,
        'width': 'auto',
    },
}

# Crispy Configuration
# https://django-crispy-forms.readthedocs.io/en/latest/

CRISPY_ALLOWED_TEMPLATE_PACKS = ('bootstrap4', 'bootstrap5')

CRISPY_TEMPLATE_PACK = 'bootstrap5'

# RestFramework Configuration
# https://www.django-rest-framework.org/

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    # Versioning configuration
    # https://www.django-rest-framework.org/api-guide/versioning/#configuring-the-versioning-scheme
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.AcceptHeaderVersioning',
    'DEFAULT_VERSION': '1',
    'ALLOWED_VERSIONS': ['1'],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 30,
}

# Settings for drf_spectacular
# https://drf-spectacular.readthedocs.io/en/latest/settings.html

SPECTACULAR_SETTINGS = {
    'TITLE': 'Oil & Rope API',
    'DESCRIPTION': 'Online roleplay easy and intuitive. Now API!',
    'VERSION': REST_FRAMEWORK['DEFAULT_VERSION'],
    'SERVE_INCLUDE_SCHEMA': False,
    'SERVE_PUBLIC': True,
    'SERVE_PERMISSIONS': ['rest_framework.permissions.AllowAny'],
}

# Email System
# https://docs.djangoproject.com/en/stable/ref/settings/#email-host

DEFAULT_FROM_EMAIL = 'oilandropeteam@gmail.com'
EMAIL_SUBJECT_PREFIX = '[Oil & Rope] '
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_PORT = os.getenv('EMAIL_PORT', '25')
EMAIL_USE_TLS = to_bool(os.getenv('EMAIL_USE_TLS', 'True'))

# CORS System
# https://github.com/adamchainz/django-cors-headers#configuration

CORS_ALLOW_ALL_ORIGINS = True

# https://github.com/adamchainz/django-cors-headers#cors_allow_methods

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# https://github.com/adamchainz/django-cors-headers#cors_urls_regex

CORS_URLS_REGEX = r'^/api/.*$'

# https://github.com/adamchainz/django-cors-headers#cors_allow_headers

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# https://github.com/adamchainz/django-cors-headers#cors_allow_credentials-bool

CORS_ALLOW_CREDENTIALS = True

# Configuration for Django Allauth
# https://django-allauth.readthedocs.io/en/latest/configuration.html

ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'

# Provider specific settings
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
            'https://www.googleapis.com/auth/calendar.events',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
    },
}

# Discord

DISCORD_API_URL = 'https://discord.com/api/v10'

# Bot Settings

BOT_INVITATION = os.getenv(
    'BOT_INVITATION',
    'https://discordapp.com/oauth2/authorize?client_id=474894488591007745&permissions=201337920&scope=bot'
)
BOT_TOKEN = os.getenv('BOT_TOKEN')
BOT_COMMAND_PREFIX = os.getenv('BOT_COMMAND_PREFIX', '..')
BOT_DESCRIPTION = os.getenv('BOT_DESCRIPTION', 'Oil & Rope Bot: Managing sessions was never this easy!')

# Extra stuff just for fun
SLOGANS = (
    'Being Ahead through Natural 20',
    'I\'m Rollin\' it',
    'I\'m Oilin\' it',
    'Rol Runs on Oil&Rope',
    'Stronger than Rope',
    'Sheer Rolling Pleasure',
    'Rol It Your Way',
    'It keeps rolling... and rolling... and rolling',
    'The Relentless Pursuit of Oil & Rope',
    'Taste the Oil',
    'Just Roll It',
    'Where\'s the Oil?',
)

# Tabletop
TABLETOP_URL = os.getenv('TABLETOP_URL', 'https://play.oilandrope-project.com')
