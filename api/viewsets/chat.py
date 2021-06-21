from django.apps import apps
from rest_framework import viewsets
from rest_framework.settings import api_settings

from common.constants import models

from ..serializers.chat import ChatSerializer

Chat = apps.get_model(models.CHAT_MODEL)


class ChatViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for :class:`Chat`.
    """

    permission_classes = api_settings.DEFAULT_PERMISSION_CLASSES
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
