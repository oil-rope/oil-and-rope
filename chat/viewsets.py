from rest_framework import viewsets

from .models import Chat
from .models import ChatMessage
from .permissions import IsModelOwner
from .serializers import ChatMessageSerializer, ChatSerializer


class ChatViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Viewset for :class:`Chat`
    """

    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    permission_classes = [IsModelOwner]


class ChatMessageViewSet(viewsets.ReadONlyModelViewSet):
    """
    Viewsets for :class:`ChatMessage`
    """

    queryset = ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer
    permission_classes = [IsModelOwner]
    