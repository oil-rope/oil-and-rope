from channels.db import database_sync_to_async

from core.consumers import HandlerJsonWebsocketConsumer

from . import models, serializers


class ChatConsumer(HandlerJsonWebsocketConsumer):
    chat_group_name = None

    async def connect(self):
        await super().connect()

    async def disconnect(self, code):
        if self.chat_group_name:
            await self.channel_layer.group_discard(self.chat_group_name, self.channel_name)
        await super().disconnect(code)

    @database_sync_to_async
    def register_message(self, author_id, chat_id, message):
        message = models.ChatMessage.objects.create(
            author_id=author_id,
            chat_id=chat_id,
            message=message,
        )
        return message

    async def setup_channel_layer(self, content):
        chat_id = content['chat']
        self.chat_group_name = f'chat_{chat_id}'
        await self.channel_layer.group_add(self.chat_group_name, self.channel_name)

    async def send_message(self, content):
        user = self.scope['user']
        message = await self.register_message(user.id, content['chat'], content['message'])
        data = serializers.ChatMessageSerializer(message).data
        func = 'group_send_message'
        content = {
            'type': f'{func}',
            'message': data
        }

        await self.channel_layer.group_send(self.chat_group_name, content)

    async def group_send_message(self, content):
        message = content['message']
        await self.send_json(message)
