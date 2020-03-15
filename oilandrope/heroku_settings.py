import django_heroku

from .settings import *

DEBUG = True

django_heroku.settings(locals(), allowed_hosts=False)
