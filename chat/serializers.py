from rest_framework import serializers

from .models import Chat
from .models import ChatMessage


class ChatSerializer(serializers.ModelSerializer):
    """
    Api serializer for :class:`User`
    """

    class Meta:
        model = Chat


class ChatMessageSerializer(serializers.ModelSerializer):
    """
    Api serializer for :class:`User`
    """

    class Meta:
        model = ChatMessage
