import logging

from channels.auth import login
from channels.db import database_sync_to_async
from django.apps import apps
from django.contrib.auth.models import AnonymousUser

from api.serializers.chat import NestedChatMessageSerializer
from common.constants import models as constants
from core.consumers import HandlerJsonWebsocketConsumer

from . import models

LOGGER = logging.getLogger(__name__)

ChatMessage = apps.get_model(constants.CHAT_MESSAGE_MODEL)
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

    @database_sync_to_async
    def get_serialized_message(self, message):
        serialized_message = NestedChatMessageSerializer(message)
        data = serialized_message.data
        return data

    @database_sync_to_async
    def get_user_by_token(self, token):
        user = User.objects.get(
            auth_token__key=token
        )
        return user

    async def setup_channel_layer(self, content):
        required_params = ('token', 'chat')
        if not all(key in content for key in required_params):
            params = ', '.join(required_params)
            msg = '%s are required.' % params
            await self.send_json({
                'type': 'info',
                'status': 'error',
                'content': msg,
            }, close=True)
        else:
            try:
                # Everything is based on RestFramework's Token
                token = content['token']
                self.user = await self.get_user_by_token(token)
                await login(scope=self.scope, user=self.user, backend=self.SESSION_BACKEND)
                await database_sync_to_async(self.scope['session'].save)()

                chat_id = content['chat']
                self.chat_group_name = f'chat_{chat_id}'
                await self.channel_layer.group_add(self.chat_group_name, self.channel_name)
                await self.send_json({
                    'type': 'info',
                    'status': 'ok',
                    'content': 'Chat connected!'
                })
            except User.DoesNotExist:
                await self.send_json({
                    'type': 'info',
                    'status': 'error',
                    'content': 'There isn\'t any user with this token.'
                }, close=True)

    async def send_message(self, content):
        if not self.user.is_authenticated:
            await self.send_json({
                'type': 'info',
                'status': 'error',
                'content': 'User is not authenticated.'
            }, close=True)
        else:
            chat_id = content['chat']
            msg_text = content['message']
            message = await self.register_message(self.user.id, chat_id, msg_text)
            serialized_message = await self.get_serialized_message(message)

            func = 'group_send_message'
            content = {
                'type': func,
                'status': 'ok',
                'content': serialized_message,
            }

            await self.channel_layer.group_send(self.chat_group_name, content)

    async def group_send_message(self, content):
        message = content['content']
        func = 'send_message'
        await self.send_json({
            'type': func,
            'status': 'ok',
            'content': message
        })
