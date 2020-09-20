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
    def register_message(self, author, chat_id, message):
        message = models.ChatMessage.objects.create(
            author=author,
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
        chat_id = content['chat']
        msg_text = content['message']
        message = await self.register_message(user, chat_id, msg_text)
        data = serializers.ChatMessageSerializer(message).data
        func = 'group_send_message'
        content = {
            'type': f'{func}',
            'message': data
        }

        try:
            await self.channel_layer.group_send(self.chat_group_name, content)
        except TypeError:
            # We send error message with serialized message and remove
            await self.send_json(
                {'error': 'We couldn\'t send your message', 'message': data},
                close=True
            )
            message.delete()

    async def group_send_message(self, content):
        message = content['message']
        await self.send_json({'message': message})
