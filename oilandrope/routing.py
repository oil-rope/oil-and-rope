from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import re_path

<<<<<<< HEAD
import chat.routing
import bot.routing
=======
from bot import consumers as bot_consumers
>>>>>>> 50f33f5822c47c46c46d683f2af391fe1f57c21a

websocket_urlpatterns = bot.routing.urlpatterns + chat.routing.websocket_urlpatterns


application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
<<<<<<< HEAD
        URLRouter(
            websocket_urlpatterns
        )
=======
        URLRouter([
            re_path(r'^ws/bot/register/$', bot_consumers.BotConsumer)
        ])
>>>>>>> 50f33f5822c47c46c46d683f2af391fe1f57c21a
    )
})
