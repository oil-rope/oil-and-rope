from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import re_path

from bot import consumers as bot_consumers
from chat import consumers as chat_consumers

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter([
            re_path(r'^ws/bot/register/$', bot_consumers.BotConsumer),
            re_path(r'^ws/chat/(?P<room_name>\w+)/$', chat_consumers.ChatConsumer),
            re_path(r'^ws/chat/$', chat_consumers.ChatRooms),
        ])
    )
})
