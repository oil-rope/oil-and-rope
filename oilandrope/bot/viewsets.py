from rest_framework import viewsets

from .models import (DiscordServer, DiscordTextChannel, DiscordUser,
                     DiscordVoiceChannel)
from .serializers import (DiscordServerSerializer,
                          DiscordTextChannelSerializer, DiscordUserSerializer,
                          DiscordVoiceChannelSerializer)


class DiscordServerViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for :class:`DiscordServer`.
    """

    queryset = DiscordServer.objects.all()
    serializer_class = DiscordServerSerializer


class DiscordTextChannelViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for :class:`DiscordTextChannel`.
    """

    queryset = DiscordTextChannel.objects.all()
    serializer_class = DiscordTextChannelSerializer


class DiscordUserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for :class:`DiscordUser`.
    """

    queryset = DiscordUser.objects.all()
    serializer_class = DiscordUserSerializer


class DiscordVoiceChannelViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for :class:`DiscordVoiceChannel`.
    """

    queryset = DiscordVoiceChannel.objects.all()
    serializer_class = DiscordVoiceChannelSerializer
