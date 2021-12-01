#!/usr/bin/env python

import multiprocessing
import os
from distutils.util import strtobool as to_bool

wsgi_module = os.getenv('GUNICORN_WSGI_MODULE', 'gunicorn_conf')
wsgi_app = f'{wsgi_module}:application'

daemon = True
reload = True
debug = bool(to_bool(os.getenv('DEBUG', 'False')))
workers = multiprocessing.cpu_count() * 2 + 1

accesslog = os.getenv('GUNICORN_ACCESS_LOGFILE', '-')
errorlog = os.getenv('GUNICORN_ERROR_LOGFILE', '-')

if debug:
    loglevel = 'debug'

if 'GUNICORN_SOCK' in os.environ:
    bind = 'unix:{socket}'.format(socket=os.getenv('GUNICORN_SOCK'))
else:
    bind = '{ip}:{port}'.format(ip=os.getenv('GUNICORN_IP', '0.0.0.0'), port=os.getenv('GUNICORN_PORT', 8000))

if all(k in os.environ for k in ('GUNICORN_CERTFILE', 'GUNICORN_KEYFILE')):
    certfile = os.getenv('GUNICORN_CERTFILE')
    keyfile = os.getenv('GUNICORN_KEYFILE')
