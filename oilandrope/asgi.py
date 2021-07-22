import django
from channels.auth import AuthMiddlewareStack
from channels.http import AsgiHandler
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.urls import re_path

django.setup()

from chat.consumers import ChatConsumer  # noqa: E402

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
