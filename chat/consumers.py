import logging

from channels.auth import get_user
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser

from core.consumers import HandlerJsonWebsocketConsumer

from . import models, serializers

LOGGER = logging.getLogger(__name__)


class ChatConsumer(HandlerJsonWebsocketConsumer):
    user = AnonymousUser()
    chat_group_name = None

    async def connect(self):
        await super().connect()
        self.user = await get_user(self.scope)

        if self.user.is_authenticated:
            LOGGER.info('User %s connected.', self.user.username)
        else:
            LOGGER.info('Anonymous user connected.')

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
        user = self.user
        chat_id = content['chat']
        msg_text = content['message']
        message = await self.register_message(user.id, chat_id, msg_text)
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
        except Exception:
            LOGGER.exception('Something went really wrong')

    async def group_send_message(self, content):
        message = content['message']
        await self.send_json({'message': message})
