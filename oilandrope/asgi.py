from channels.auth import AuthMiddlewareStack
from channels.routing import AsgiHandler, ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

from bot.routing import websocket_urlpatterns as bot_ws_urls
from chat.routing import websocket_urlpatterns as chat_ws_urls


def get_all_websocket_urlpatterns():
    """
    Simple function to get everything inside a list.
    """

    return bot_ws_urls + chat_ws_urls


application = ProtocolTypeRouter({
    'http': AsgiHandler(),
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                get_all_websocket_urlpatterns()
            )
        )
    )
})
