from rest_framework import viewsets
from . import models, serializers


class ChatViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Chat.objects.all()
    serializer_class = serializers.ChatSerializer
