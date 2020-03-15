import django_heroku

from .settings import *

django_heroku.settings(locals(), databases=False, allowed_hosts=False, secret_key=False)
