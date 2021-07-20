from django.apps import apps
from rest_framework import serializers

from common.constants import models

from .common import MappedSerializerMixin
from .registration import SimpleUserSerializer

ChatMessage = apps.get_model(models.CHAT_MESSAGE_MODEL)
Chat = apps.get_model(models.CHAT_MODEL)


class ChatMessageSerializer(MappedSerializerMixin, serializers.ModelSerializer):
    serializers_map = {
        'author': SimpleUserSerializer(many=False, read_only=True)
    }

    class Meta:
        model = ChatMessage
        fields = (
            'id', 'chat', 'message', 'author', 'entry_created_at', 'entry_updated_at',
        )


class ChatSerializer(serializers.ModelSerializer):
    chat_message_set = ChatMessageSerializer(many=True)

    class Meta:
        model = Chat
        fields = (
            'id', 'name', 'users', 'chat_message_set', 'entry_created_at', 'entry_updated_at',
        )
