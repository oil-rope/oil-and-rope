from django.urls import include, path
from rest_framework import routers

from . import viewsets

router = routers.DefaultRouter()
router.register(r'discord_user', viewsets.DiscordUserViewSet)
router.register(r'discord_server', viewsets.DiscordServerViewSet)
router.register(r'discord_text_channel', viewsets.DiscordTextChannelViewSet)
router.register(r'discord_voice_channel', viewsets.DiscordVoiceChannelViewSet)

app_name = 'bot'

urlpatterns = [
    # WebSockets
    path('', include('bot.routing')),
    path('api/', include(router.urls)),
]
