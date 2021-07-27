from pathlib import Path

import django
from channels.auth import AuthMiddlewareStack
from channels.http import AsgiHandler
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.urls import re_path

from common.utils.env import load_env_file

django.setup()

from chat.consumers import ChatConsumer  # noqa: E402

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / '.env'
load_env_file(ENV_FILE)

application = ProtocolTypeRouter({
        'http': AsgiHandler(),
        'websocket': AllowedHostsOriginValidator(
            AuthMiddlewareStack(
                URLRouter([
                    re_path(r'^ws/chat/$', ChatConsumer.as_asgi(), name='connect',),
                ])
            )
        )
    })
