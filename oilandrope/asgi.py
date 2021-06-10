"""
ASGI entrypoint. Configures Django and then runs the application
defined in the ASGI_APPLICATION setting.
"""

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

from bot.routing import websocket_urlpatterns as bot_ws_urls
from chat.routing import websocket_urlpatterns as chat_ws_urls


def get_all_websocket_urlpatterns():
    """
    Simple function to get everything inside a list.
    """

    return bot_ws_urls + chat_ws_urls


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "oilandrope.settings")
application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(
            get_all_websocket_urlpatterns()
        )
    )
})
