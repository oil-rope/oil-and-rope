"""
WSGI config for oilandrope project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
import dotenv

ENV_FILE = Path(os.path.join(os.path.dirname(os.path.dirname(__file__)))) / '.env'
if not ENV_FILE.is_file() or not ENV_FILE.exists():
    raise FileNotFoundError('File \'.env\' doesn\'t exist, please create one by copying \'.env.example\'')

dotenv.load_dotenv(ENV_FILE, override=True, verbose=True, encoding='utf-8')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oilandrope.settings')

application = get_wsgi_application()
