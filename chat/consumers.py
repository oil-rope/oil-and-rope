import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User

from registration.serializers import UserSerializer

from . import models
from .serializers import ChatMessageSerializer, ChatSerializer


class ChatConsumer(AsyncWebsocketConsumer):
    """
    Consumer for chat
    """

    def __init__(self, *args, **kwargs):
        super(ChatConsumer, self).__init__(*args, **kwargs)

        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group = 'board_{}'.format(self.room_name)

    async def connect(self):
        await self.channel_layer.group_add(
            self.room_group,
            self.channel_name
        )

        await self.accept()
        await self.recover_chat_messages()

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

        chat, created = models.Chat.objects.get_or_create(name=chat_pk)
        chat.users.add(user)
        chat_msg_sender = User.objects.get(pk=owner_pk)

        owner_json = UserSerializer(chat_msg_sender, many=False).data
        chat_json = ChatSerializer(chat, many=False).data

        await self.channel_layer.group_send(
            self.room_group,
            {
                'type': 'chat_message',
                'chat': chat_json,
                'message': message_str,
                'owner': owner_json,
                'created_at': created_at,

            }
        )

    async def chat_message(self, event):
        
        chat_json = event['chat']
        message = event['message']
        owner_json = event['owner']
        created_at = event['created_at']

        user = self.scope['user']

        chat = models.Chat.objects.get(id=chat_json['id'])
        owner = User.objects.get(id=owner_json['id'])

        own_message = True if owner.id == user.id else False

        if own_message:
            await self.save_to_db(chat, message, owner, created_at)

        # message_json = ChatMessageSerializer(chat_message).data

        message_json = {
            'chat': chat_json,
            'message': message,
            'user': owner.username,
            'created_at': created_at,
        }

        await self.send(text_data=json.dumps({
            'message': message_json,
            'own_message': own_message,
        }))

    @database_sync_to_async
    def save_to_db(self, chat, message, owner, created_at):
        chat_message, created = models.ChatMessage.objects.get_or_create(
            chat=chat,
            message=message,
            user=owner,
            created_at=created_at,
        )

    async def recover_chat_messages(self):

        user = self.scope['user']

        chat = models.Chat.objects.get(id=self.room_name)
        chat_json = ChatSerializer(chat, many=False).data

        messages = models.ChatMessage.objects.all()

        for message in messages:

            message_json = {
                'chat': chat_json,
                'message': message.message,
                'user': message.user.username,
                'created_at': str(message.created_at),
            }

            if user.id == message.user.id:
                own_message = True
            else:
                own_message = False

            await self.send(text_data=json.dumps({
                'message': message_json,
                'own_message': own_message,
            }))


class ChatRooms(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super(ChatConsumer, self).__init__(*args, **kwargs)

        self.room_name = 'rooms'
        self.room_group = 'chats_{}'.format(self.room_name)

    async def connect(self):
        await self.channel_layer.group_add(
            self.room_group,
            self.channel_name
        )

        await self.accept("subprotocol")
        # To reject the connection, call:

        await self.show_rooms()

        await self.close()

    async def receive(self, text_data=None, bytes_data=None):
        # Called with either text_data or bytes_data for each frame
        # You can call:
        await self.send(text_data="Hello world!")
        # Or, to send a binary frame:
        await self.send(bytes_data="Hello world!")
        # Want to force-close the connection? Call:
        await self.close()
        # Or add a custom WebSocket error code!
        await self.close(code=4123)

    async def show_rooms(self):

        user = self.scope['user']

        chats = user.chats.all()

        chats_serialized = ChatSerializer(chats, many=True)

        await self.send(text_data=json.dumps({
            'chats': chats_serialized
        }))

    async def disconnect(self, close_code):
        # Called when the socket closes
        await self.channel_layer.group_discard(
            self.room_group,
            self.channel_name
        )
