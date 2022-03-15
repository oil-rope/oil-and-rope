from .settings import *

# Dummy KEY needed by python
SECRET_KEY = 'de68z30c(3nbj*k4=lumea8hztcy_6%d0epx^w$jc&s)wygezo'

DEBUG = True
ALLOWED_HOSTS = []

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'oilandrope.sqlite3',
        'TEST': {
            'NAME': 'test_oilandrope.sqlite3'
        },
    },
}

INSTALLED_APPS.extend([
    'django_extensions',
    'debug_toolbar',
])

MIDDLEWARE.extend([
    'debug_toolbar.middleware.DebugToolbarMiddleware',
])

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('127.0.0.1', 6379)],
        },
    },
}

SHELL_PLUS_PRINT_SQL = True
SHELL_PLUS_IMPORTS = [
    'from bot.enums import ChannelTypes, EmbedTypes, HttpMethods, MessageTypes',
    'from common.enums import AvailableIcons, JavaScriptAction',
    'from dynamic_menu.enums import MenuTypes',
    'from roleplay.enums import DomainTypes, RoleplaySystems, SiteTypes',
]
