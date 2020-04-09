"""
Django settings for oilandrope project.

Generated by 'django-admin startproject' using Django 2.2.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os

from django.utils.translation import gettext_lazy as _

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = [
    'oil-and-rope.herokuapp.com',
]

# Defines Admins
# https://docs.djangoproject.com/en/2.2/ref/settings/#admins

ADMINS = [
    ('LeCuay', 'suso.becerra98@gmail.com'),
    ('Daniel', 'danielpaz4c@gmail.com'),
]

# Defines Manager
# https://docs.djangoproject.com/en/2.2/ref/settings/#managers

MANAGERS = ADMINS

# Application definition

INSTALLED_APPS = [
    # Dynamic translation (https://django-modeltranslation.readthedocs.io/)
    # Must be setted before 'django.contrib.admin' to work correctly on admin
    'modeltranslation',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # The “sites” framework (https://docs.djangoproject.com/en/2.2/ref/contrib/sites/)
    'django.contrib.sites',
    # Model-Bootstrap Forms (https://django-crispy-forms.readthedocs.io/)
    'crispy_forms',
    # Multiple Forms Tools (https://django-formtools.readthedocs.io/)
    'django_tables2',
    # CKEditor's RichText (https://django-ckeditor.readthedocs.io/en/latest/)
    'ckeditor',
    # API RestFramework (https://www.django-rest-framework.org/)
    'rest_framework',
    # DjangoMptt (https://django-mptt.readthedocs.io/)
    'mptt',
    # Source
    'core.apps.CoreConfig',
    # Dynamic Menu
    'dynamic_menu.apps.DynamicMenuConfig',
    # Bot
    'bot.apps.BotConfig',
    # Registration System
    'registration.apps.RegistrationConfig',
    # Chat
    'chat.apps.ChatConfig',
    # Sheet
    'sheet.apps.SheetConfig',
    # FrontEnd
    'frontend.apps.FrontendConfig',
    # Django channels
    'channels'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'dynamic_menu.middleware.DynamicMenuMiddleware',
]

# SITE_ID = 1 is for declaring page ID
# (https://docs.djangoproject.com/en/2.2/ref/contrib/sites/#enabling-the-sites-framework)

SITE_ID = 1

ROOT_URLCONF = 'oilandrope.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'email/templates/')
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.language',
                'dynamic_menu.context_processors.menus',
            ],
        },
    },
]

WSGI_APPLICATION = 'oilandrope.wsgi.application'

ASGI_APPLICATION = 'oilandrope.routing.application'
# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'oilandrope'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', '127.0.0.1'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'TEST': {
            'NAME': os.getenv('DB_TEST_NAME', 'test_{}'.format(os.getenv('DB_NAME', 'oilandrope')))
        },
    },
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en'

# Supported languages
# https://docs.djangoproject.com/en/2.2/ref/settings/#languages

LANGUAGES = [
    ('en', _('English')),
    ('es', _('Spanish')),
]

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Translation files

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale')
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

# Login System
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth

LOGIN_REDIRECT_URL = 'core:home'
LOGOUT_REDIRECT_URL = 'registration:login'

# Media files
# https://docs.djangoproject.com/en/2.2/ref/settings/#media-root

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

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
            ['RemoveFormat', 'Source'],
        ],
    },
}

# Crispy Configuration
# https://django-crispy-forms.readthedocs.io

CRISPY_TEMPLATE_PACK = 'bootstrap4'

# RestFramwork Configuration
# https://www.django-rest-framework.org/

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
}


# Redis 
# https://pypi.org/project/channels-redis/

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}

# Email System
# https://docs.djangoproject.com/en/2.2/ref/settings/#email-host

DEFAULT_FROM_EMAIL = 'oilandropeteam@gmail.com'
EMAIL_SUBJECT_PREFIX = '[Oil & Rope] '
EMAIL_HOST = os.getenv('EMAIL_HOST', 'localhost')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
EMAIL_PORT = os.getenv('EMAIL_PORT', '25')
EMAIL_USE_TLS = True
