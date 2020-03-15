import django_heroku

from .settings import *

django_heroku.settings(locals(), allowed_hosts=False)
