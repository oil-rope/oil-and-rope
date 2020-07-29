from .settings import *

# Dummy KEY needed by python
SECRET_KEY = 'de68z30c(3nbj*k4=lumea8hztcy_6%d0epx^w$jc&s)wygezo'

DEBUG = True

if 'ALLOWED_HOSTS' in os.environ:
    ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'oil-and-rope.herokuapp.com').split(',')
else:
    ALLOWED_HOSTS = []

INTERNAL_IPS = (
    '127.0.0.1',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.getenv('DB_NAME', 'oilandrope') + '.sqlite3',
        'TEST': {
            'NAME': os.getenv('DB_TEST_NAME', 'test_{}.sqlite3'.format(os.getenv('DB_NAME', 'oilandrope')))
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

# Django PDB has special behaviour
INSTALLED_APPS.insert(0, 'django_pdb')
MIDDLEWARE.append('django_pdb.middleware.PdbMiddleware')

EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.mailtrap.io')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'user@mailtrap')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', 'mailtrap_p4ssw0rd')
EMAIL_PORT = os.getenv('EMAIL_PORT', '2525')
EMAIL_USE_TLS = False

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('127.0.0.1', 6379)],
        },
    },
}
