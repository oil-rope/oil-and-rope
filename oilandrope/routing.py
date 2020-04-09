from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

import chat.routing
import bot.routing

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter([
            bot.routing.urlpatterns,
            chat.routing.websocket_urlpatterns,
        ]
        )
    )
})
