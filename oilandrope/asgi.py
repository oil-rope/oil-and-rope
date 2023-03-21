from pathlib import Path

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application
from django.urls import re_path

from common.utils.env import load_env_file, load_secrets

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / '.env'
load_env_file(ENV_FILE)
load_secrets()

django_asgi_app = get_asgi_application()

from chat.consumers import ChatConsumer  # noqa: E402

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter([
                re_path(r'^ws/chat/$', ChatConsumer.as_asgi(), name='connect',),
            ]),
        ),
    ),
})
