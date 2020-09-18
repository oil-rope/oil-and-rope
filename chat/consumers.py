from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async

from core.consumers import HandlerJsonWebsocketConsumer

from . import models, serializers


class ChatConsumer(HandlerJsonWebsocketConsumer):
    chat_group_name = None
    chat = None

    async def connect(self):
        await super().connect()

    async def receive_json(self, content, **kwargs):
        func = content['type']
        if func == 'setup_channel_layer':
            await super().receive_json(content, **kwargs)
        else:
            user = self.scope['user']
            content['user'] = user.id
            content['chat_message_next_pk'] = await self.get_chat_message_next_primary_key()
            await self.channel_layer.group_send(self.chat_group_name, content)

    async def disconnect(self, code):
        if self.chat_group_name:
            await self.channel_layer.group_discard(self.chat_group_name, self.channel_name)
        await super().disconnect(code)

    @database_sync_to_async
    def get_chat_message_next_primary_key(self):
        next_pk = 1
        chat_messages = models.ChatMessage.objects.all()
        if chat_messages:
            next_pk = chat_messages.order_by('pk').last().pk + 1
        return next_pk

    async def setup_channel_layer(self, content):
        chat_id = content['chat']
        self.chat_group_name = f'chat_{chat_id}'
        await self.channel_layer.group_add(self.chat_group_name, self.channel_name)

    async def send_message(self, content):
        message, created = models.ChatMessage.objects.get_or_create(
            id=content['chat_message_next_pk'],
            defaults={
                'author_id': content['user'],
                'chat_id': content['chat'],
                'message': content['message']
            }
        )
        data = serializers.ChatMessageSerializer(message).data

        await self.send_json(data)
