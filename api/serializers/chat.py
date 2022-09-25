from rest_framework import serializers

from chat.models import Chat, ChatMessage

from .common import WebSocketMessageSerializer
from .registration import SimpleUserSerializer


class ChatMessageSerializer(serializers.ModelSerializer):
    author = author = SimpleUserSerializer(many=False, read_only=True, default=serializers.CurrentUserDefault())

    class Meta:
        model = ChatMessage
        fields = (
            'id', 'chat', 'message', 'author', 'entry_created_at', 'entry_updated_at',
        )


class ChatMessageCreateRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ('message',)


class ChatMessageUpdateRequestSerializer(ChatMessageCreateRequestSerializer):
    pass


class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = (
            'id', 'name', 'users', 'chat_message_set', 'entry_created_at', 'entry_updated_at',
        )


class WebSocketChatSerializer(WebSocketMessageSerializer):
    chat = serializers.PrimaryKeyRelatedField(
        queryset=Chat.objects.all(),
        required=True,
    )
    message = serializers.CharField(max_length=255, required=False)
    content = ChatMessageSerializer(many=False, read_only=True)
