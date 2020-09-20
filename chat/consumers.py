import logging

from channels.auth import login
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.models import Session

from common.tools.sync import async_get
from core.consumers import HandlerJsonWebsocketConsumer

from . import models, serializers

LOGGER = logging.getLogger(__name__)


class ChatConsumer(HandlerJsonWebsocketConsumer):
    user = AnonymousUser()
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
        try:
            # Since Hosts can be different due to 'live.oilandrope-project.com' we get
            # user from Session instead from Middleware
            session = await async_get(Session, pk=content['session_key'])
            session_data = session.get_decoded()
            user = await async_get(get_user_model(), pk=session_data['_auth_user_id'])
            self.user = user
            await login(self.scope, user)
            await database_sync_to_async(self.scope["session"].save)()
        except (Session.DoesNotExist, get_user_model().DoesNotExist, KeyError):
            self.user = AnonymousUser()
        finally:
            chat_id = content['chat']
            self.chat_group_name = f'chat_{chat_id}'
            await self.channel_layer.group_add(self.chat_group_name, self.channel_name)

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
