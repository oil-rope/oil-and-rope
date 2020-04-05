import json
import os
import re
import time
import uuid

from channels.db import database_sync_to_async
from channels.generic.webwsocket import AsyncWebSocketConsumer
from django import db
from django.contrib.auth.models import User
from django.db import transaction

from registration.serializers import ProfileSerializer, UserSerializer

from . import models
from .serializers import ChatMessageSerializer, ChatSerializer


class ChatConsumer(AsyncWebSocketConsumer):
    """
    Consumer for chat
    """

    def __init__(self, *args, **kwargs):
        super(ChatConsumer, self).__init__(*args, **kwargs)

        self.room_name = self.scope['url_route']['kwargs']['chat']
        self.room_group = 'board_{}'.format(self.room_name)

    async def connect(self):
        await self.channel_layer.group_add(
            self.room_group,
            self.channel_name
        )

        await self.accept()

        # user = self.scope['user']
        # chats = user.Profile.objects.all()
        # user_json = UserSerializer(user, many=False).data

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.room_group,
            self.channel_name
        )

    async def receive(self, text_data=None, bytest_data=None):

        user = self.scope['user']
        text_data_json = json.loads(text_data)

        owner_pk = text_data_json.get('user')
        chat_pk = text_data_json.get('chat', '')
        message_str = text_data_json.get('message', '')
        created_at = text_data_json.get('created_at')

        chat = user.chats.get(pk=chat_pk)
        chat_msg_sender = User.objects.get(pk=owner_pk)

        owner_json = UserSerializer(chat_msg_sender, many=False)
        chat_json = ChatSerializer(chat, many=False)

        await self.channel_layer.group_send(
            self.room_group,
            {
                'chat': chat_json,
                'message': message_str,
                'owner': owner_json,
                'created_at': created_at,

            }
        )

    @transaction.atomic
    async def chat_message(self, event):
        chat = event['chat']
        message = event['message']
        owner = event['owner']
        created_at = event['created_at']

        user = self.scope['user']

        own_message = True if owner == user.id else False

        chat_message, created = models.ChatMessage.objects.get_or_create(
            chat=chat,
            message=message,
            user=owner,
            created_at=created_at,
        )

        message_json = ChatMessageSerializer(chat_message).data
        owner_json = UserSerializer(owner)

        await self.send(text_data=json.dumps({
            'message': message_json,
            'chat': chat,
            'user': owner_json,
            'owner': event['owner'],
            'created_at': created_at,
            'own_message': own_message,
        }))
