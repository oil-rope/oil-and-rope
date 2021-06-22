from rest_framework import viewsets
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.settings import api_settings

from .models import DiscordServer, DiscordTextChannel, DiscordUser, DiscordVoiceChannel
from .serializers import (DiscordServerSerializer, DiscordTextChannelSerializer, DiscordUserSerializer,
                          DiscordVoiceChannelSerializer)


class DiscordServerViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for :class:`DiscordServer`.
    """

    permission_classes = api_settings.DEFAULT_PERMISSION_CLASSES + [DjangoModelPermissions]
    queryset = DiscordServer.objects.all()
    serializer_class = DiscordServerSerializer


class DiscordTextChannelViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for :class:`DiscordTextChannel`.
    """

    permission_classes = api_settings.DEFAULT_PERMISSION_CLASSES + [DjangoModelPermissions]
    queryset = DiscordTextChannel.objects.all()
    serializer_class = DiscordTextChannelSerializer


class DiscordUserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for :class:`DiscordUser`.
    """

    permission_classes = api_settings.DEFAULT_PERMISSION_CLASSES + [DjangoModelPermissions]
    queryset = DiscordUser.objects.all()
    serializer_class = DiscordUserSerializer


class DiscordVoiceChannelViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for :class:`DiscordVoiceChannel`.
    """

    permission_classes = api_settings.DEFAULT_PERMISSION_CLASSES + [DjangoModelPermissions]
    queryset = DiscordVoiceChannel.objects.all()
    serializer_class = DiscordVoiceChannelSerializer
