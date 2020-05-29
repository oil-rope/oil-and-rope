#!/usr/bin/env python

import multiprocessing
import os
from distutils.util import strtobool as to_bool

accesslog = os.getenv('GUNICORN_ACCESS_LOGFILE', '-')
errorlog = os.getenv('GUNICORN_ERROR_LOGFILE', '-')
if 'GUNICORN_SOCK' in os.environ:
    bind = 'unix:{socket}'.format(socket=os.getenv('GUNICORN_SOCK'))
else:
    bind = '{ip}:{port}'.format(ip=os.getenv('GUNICORN_IP', '0.0.0.0'), port=os.getenv('GUNICORN_PORT', 8000))
daemon = True
reload = bool(to_bool(os.getenv('DEBUG', 'False')))
workers = multiprocessing.cpu_count() * 2 + 1
if all(k in os.environ for k in ('GUNICORN_CERTFILE', 'GUNICORN_KEYFILE')):
    certfile = os.getenv('GUNICORN_CERTFILE')
    keyfile = os.getenv('GUNICORN_KEYFILE')
