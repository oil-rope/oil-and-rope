"""
WSGI config for oilandrope project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""

import os
from pathlib import Path

import dotenv
from django.core.wsgi import get_wsgi_application

from common.utils.env import load_env_file

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / '.env'
load_env_file(ENV_FILE)

dotenv.load_dotenv(ENV_FILE, override=True, verbose=True, encoding='utf-8')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oilandrope.settings')

application = get_wsgi_application()
