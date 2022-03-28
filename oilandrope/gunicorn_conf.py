#!/usr/bin/env python

import multiprocessing
import os
from distutils.util import strtobool as to_bool
from pathlib import Path

from common.utils.env import load_env_file

# If we load `.env` here we'll avoid loading it in each worker process
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / '.env'
load_env_file(ENV_FILE)

# NOTE: We use `os.environ` to ensure that those variables are set

wsgi_module = os.environ['GUNICORN_WSGI_MODULE']
wsgi_app = f'{wsgi_module}:application'

daemon = bool(to_bool(os.environ['GUNICORN_DAEMON']))
reload = True
debug = bool(to_bool(os.environ['DEBUG'], 'False'))

if 'GUNICORN_WORKERS' in os.environ:
    workers = int(os.environ['GUNICORN_WORKERS'])
else:
    workers = multiprocessing.cpu_count() * 2 + 1

accesslog = os.environ['GUNICORN_ACCESS_LOGFILE']
errorlog = os.environ['GUNICORN_ERROR_LOGFILE']

if debug:
    loglevel = 'debug'

if 'GUNICORN_SOCK' in os.environ and os.environ['GUNICORN_SOCK']:
    bind = 'unix:{socket}'.format(socket=os.environ['GUNICORN_SOCK'])
else:
    bind = '{ip}:{port}'.format(
        ip=os.environ['GUNICORN_IP'],
        port=os.environ['GUNICORN_PORT'],
    )

if all(k in os.environ for k in ('GUNICORN_CERTFILE', 'GUNICORN_KEYFILE')):
    certfile = os.environ['GUNICORN_CERTFILE']
    keyfile = os.environ['GUNICORN_KEYFILE']
