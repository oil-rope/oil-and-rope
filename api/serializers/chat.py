from django.apps import apps
from django.contrib.auth import get_user_model
from rest_framework import serializers

from common.constants import models

from ..validators.chat import UserInAuthorValidator
from .registration import SimpleUserSerializer

User = get_user_model()
ChatMessage = apps.get_model(models.CHAT_MESSAGE_MODEL)
Chat = apps.get_model(models.CHAT_MODEL)


class ChatMessageSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        validators=[UserInAuthorValidator],
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        model = ChatMessage
        fields = (
            'id', 'chat', 'message', 'author', 'entry_created_at', 'entry_updated_at',
        )


class NestedChatMessageSerializer(ChatMessageSerializer):
    """
    More handy serializer for `JSON` instances. Not able to be writable.
    """

    author = SimpleUserSerializer(many=False, read_only=True, default=serializers.CurrentUserDefault())


class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = (
            'id', 'name', 'users', 'chat_message_set', 'entry_created_at', 'entry_updated_at',
        )


class NestedChatSerializer(ChatSerializer):
    chat_message_set = NestedChatMessageSerializer(many=True, read_only=True)
