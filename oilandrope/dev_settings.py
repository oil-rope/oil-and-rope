from .settings import *

# Dummy KEY needed by python
SECRET_KEY = 'de68z30c(3nbj*k4=lumea8hztcy_6%d0epx^w$jc&s)wygezo'

DEBUG = True
ALLOWED_HOSTS = []

# NOTE: Needed for `debug_toolbar`
INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
]

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

MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')


# In Memory Channel Layer for testing
# https://channels.readthedocs.io/en/stable/topics/channel_layers.html#in-memory-channel-layer

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}

SHELL_PLUS_PRINT_SQL = True
SHELL_PLUS_IMPORTS = [
    'from bot.enums import ChannelTypes, EmbedTypes, HttpMethods, MessageTypes',
    'from bot.models import User as DiscordUser, Channel as DiscordChannel, Message as DiscordMessage',
    'from common.enums import AvailableIcons, JavaScriptActions, WebSocketCloseCodes',
    'from roleplay.enums import DomainTypes, RoleplaySystems, SiteTypes',
]

# Debug Toolbar configuration
# https://django-debug-toolbar.readthedocs.io/en/latest/configuration.html

SHOW_COLLAPSED = True

ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'http'
