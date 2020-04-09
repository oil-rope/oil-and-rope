from rest_framework import serializers

from .models import Chat, ChatMessage


class ChatSerializer(serializers.ModelSerializer):
    """
    Api serializer for :class:`User`
    """

    class Meta:
        model = Chat
        fields = '__all__'


class ChatMessageSerializer(serializers.ModelSerializer):
    """
    Api serializer for :class:`User`
    """

    class Meta:
        model = ChatMessage
        fields = '__all__'
