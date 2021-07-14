import logging

from channels.auth import login
from channels.db import database_sync_to_async
from django.apps import apps
from django.contrib.auth.models import AnonymousUser
from rest_framework.authtoken.models import Token

from api.serializers.chat import ChatMessageSerializer
from common.constants import models as constants
from core.consumers import HandlerJsonWebsocketConsumer

from . import models

LOGGER = logging.getLogger(__name__)

User = apps.get_model(constants.USER_MODEL)


class ChatConsumer(HandlerJsonWebsocketConsumer):
    user = AnonymousUser()
    chat_group_name = None
    SESSION_BACKEND = 'django.contrib.auth.backends.ModelBackend'

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
        required_params = ('token', 'chat')
        if not all(key in content for key in required_params):
            params = ', '.join(required_params)
            msg = '%s are required.' % params
            await self.send_json({
                'type': 'info',
                'status': 'error',
                'content': msg,
            }, True)
        else:
            try:
                # Everything is based on RestFramework's Token
                token = await database_sync_to_async(Token.objects.get)(pk=content['token'])
                self.user = await database_sync_to_async(User.objects.get)(pk=token.user_id)
                await login(scope=self.scope, user=self.user, backend=self.SESSION_BACKEND)
                await database_sync_to_async(self.scope['session'].save)()
            except (Token.DoesNotExist, User.DoesNotExist, KeyError):
                self.user = AnonymousUser()

            chat_id = content['chat']
            self.chat_group_name = f'chat_{chat_id}'
            await self.channel_layer.group_add(self.chat_group_name, self.channel_name)
            await self.send_json({
                'type': 'info',
                'status': 'ok',
                'content': 'Chat connected!'
            })

    async def send_message(self, content):

        if not self.user.is_authenticated:
            await self.send_json(
                {'error': 'User is not authenticated.'},
                close=True
            )
        else:
            chat_id = content['chat']
            msg_text = content['message']
            message = await self.register_message(self.user.id, chat_id, msg_text)
            data = ChatMessageSerializer(message).data

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
