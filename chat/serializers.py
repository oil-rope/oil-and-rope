from rest_framework import serializers

from . import models


class ChatMessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.ChatMessage
        fields = '__all__'


class ChatSerializer(serializers.ModelSerializer):
    chat_message_set = ChatMessageSerializer(many=True)

    class Meta:
        model = models.Chat
        fields = '__all__'
