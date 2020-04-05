from django.conf.urls import url

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

from chat.consumers import AdminChatConsumer, PublicChatConsumer
from aprs_news.consumers import APRSNewsConsumer

application = ProtocolTypeRouter({

    # WebSocket chat handler
    "websocket": AuthMiddlewareStack(
        URLRouter([
            url(r"^chat/admin/$", AdminChatConsumer),
            url(r"^chat/$", PublicChatConsumer),
        ])
    ),

    # Using the third-party project frequensgi, which provides an APRS protocol
    "aprs": APRSNewsConsumer,

})
