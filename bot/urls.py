from django.urls import include, path
from rest_framework import routers

from . import views, viewsets

router = routers.DefaultRouter()
router.register(r'discord_user', viewsets.DiscordUserViewSet)
router.register(r'discord_server', viewsets.DiscordServerViewSet)
router.register(r'discord_text_channel', viewsets.DiscordTextChannelViewSet)
router.register(r'discord_voice_channel', viewsets.DiscordVoiceChannelViewSet)

app_name = 'bot'

BOT_UTILS = [
    path('send_message/', views.SendMessageToDiscordUserView.as_view(), name='send_message'),
    path('send_invitation/', views.SendInvitationView.as_view(), name='send_invitation')
]

urlpatterns = [
    path('api/', include(router.urls)),
    path('utils/', include((BOT_UTILS, app_name), namespace='utils')),
]
