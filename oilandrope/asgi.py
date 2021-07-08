"""
ASGI entrypoint. Configures Django and then runs the application
defined in the ASGI_APPLICATION setting.
"""

import os

import django
from channels.auth import AuthMiddlewareStack
from channels.http import AsgiHandler
from channels.routing import ProtocolTypeRouter, URLRouter

from bot.routing import websocket_urlpatterns as bot_ws_urls
from chat.routing import websocket_urlpatterns as chat_ws_urls

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oilandrope.settings')
django.setup()


def get_all_websocket_urlpatterns():
    """
    Simple function to get everything inside a list.
    """

    return bot_ws_urls + chat_ws_urls


application = ProtocolTypeRouter({
    'http': AsgiHandler(),
    'websocket': AuthMiddlewareStack(
        URLRouter(
            get_all_websocket_urlpatterns()
        )
    )
})
