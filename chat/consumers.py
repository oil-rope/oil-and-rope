import json
import logging

from channels.auth import login
from channels.db import database_sync_to_async
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from api.serializers.chat import ChatMessageSerializer, WebSocketChatSerializer
from chat.models import ChatMessage
from common.enums import WebSocketCloseCodes
from core.consumers import HandlerJsonWebsocketConsumer
from core.exceptions import OilAndRopeException
from registration.models import User
from roleplay.utils.dice import roll_dice

LOGGER = logging.getLogger(__name__)


class ChatConsumer(HandlerJsonWebsocketConsumer):
    user = None
    chat_group_name = None
    serializer_class = WebSocketChatSerializer

    async def disconnect(self, code):
        if self.chat_group_name:
            await self.channel_layer.group_discard(self.chat_group_name, self.channel_name)
        await super().disconnect(code)

    async def receive(self, text_data=None, bytes_data=None, **kwargs):
        json_data = json.loads(text_data)
        # Authenticating by given token
        if 'token' in json_data:
            user = await self.get_user(json_data['token'])
            if user:
                await login(self.scope, user, backend='django.contrib.auth.backends.ModelBackend')
                await database_sync_to_async(self.scope['session'].save)()

        self.user = self.scope['user']
        if not self.user.is_authenticated:
            msg = _('user not authenticated.').capitalize()
            await super().send_json({
                'type': 'info',
                'content': {'message': msg},
            })
            return await super().close(code=WebSocketCloseCodes.UNAUTHORIZED.value)
        return await super().receive(text_data, bytes_data, **kwargs)

    @database_sync_to_async
    def get_user(self, token):
        user = User.objects.filter(auth_token=token)
        if user.exists():
            return user.first()
        return None

    @database_sync_to_async
    def register_message(self, author_id: int, chat_id: int, message: str) -> ChatMessage:
        return ChatMessage.objects.create(
            author_id=author_id,
            chat_id=chat_id,
            message=message,
        )

    @database_sync_to_async
    def register_roll_message(self, chat_id: int, message: str) -> tuple[ChatMessage, dict]:
        bot = User.objects.get(email=settings.DEFAULT_FROM_EMAIL)
        try:
            result, roll = roll_dice(message)
        except OilAndRopeException as ex:
            # NOTE: If roll fails, we send message to chat with error message
            result = ex.message
            roll = {}
        finally:
            message = result
            return ChatMessage.objects.create(
                author_id=bot.id,
                chat_id=chat_id,
                message=result,
            ), dict(roll)

    @database_sync_to_async
    def get_serialized_message(self, message: ChatMessage) -> dict:
        serialized_message = ChatMessageSerializer(message)
        return serialized_message.data

    async def setup_channel_layer(self, content):
        chat_id = content['chat']
        self.chat_group_name = f'chat_{chat_id}'
        await self.channel_layer.group_add(self.chat_group_name, self.channel_name)

        return await self.send_json({
            'type': 'info',
            'content': {'message': 'Chat connected!'},
        })

    async def make_roll(self, content):
        chat_id = content['chat']
        msg_text = content['message']
        message, roll = await self.register_roll_message(chat_id, msg_text)
        serialized_message = await self.get_serialized_message(message)

        return await self.channel_layer.group_send(
            self.chat_group_name,
            {
                'type': 'group_send_message',
                'status': 'ok',
                'content': serialized_message,
                'roll': roll,
            },
        )

    async def send_message(self, content):
        chat_id = content['chat']
        msg_text = content['message']
        message = await self.register_message(self.user.id, chat_id, msg_text)
        serialized_message = await self.get_serialized_message(message)

        return await self.channel_layer.group_send(
            self.chat_group_name,
            {
                'type': 'group_send_message',
                'content': serialized_message,
            },
        )

    async def group_send_message(self, content):
        content['type'] = 'send_message'
        return await self.send_json(content)
