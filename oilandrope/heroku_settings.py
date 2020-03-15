import django_heroku

from .settings import *

DEBUG = True

django_heroku.settings(locals(), databases=False, allowed_hosts=False, secret_key=False)
