import django_heroku
from oilandrope.settings import *

django_heroku.settings(locals(), allowed_hosts=False)
