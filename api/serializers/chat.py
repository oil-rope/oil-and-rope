from typing import TYPE_CHECKING

from django.apps import apps
from django.contrib.auth import get_user_model
from rest_framework import serializers

from common.constants import models

from .common import WebSocketMessageSerializer
from .registration import SimpleUserSerializer

if TYPE_CHECKING:  # pragma: no cover
    from chat.models import Chat as ChatModel
    from chat.models import ChatMessage as ChatMessageModel
    from registration.models import User as UserModel

User: 'UserModel' = get_user_model()
ChatMessage: 'ChatMessageModel' = apps.get_model(models.CHAT_MESSAGE)
Chat: 'ChatModel' = apps.get_model(models.CHAT)


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
