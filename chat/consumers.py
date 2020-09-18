from channels.db import database_sync_to_async

from core.consumers import HandlerJsonWebsocketConsumer

from . import models, serializers


class ChatConsumer(HandlerJsonWebsocketConsumer):

    async def connect(self):
        await super().connect()

    @database_sync_to_async
    def get_chat(self, chat_pk):
        chat = models.Chat.objects.get(pk=chat_pk)
        return chat

    @database_sync_to_async
    def register_chat_message(self, chat, message, user):
        message = models.ChatMessage.objects.create(
            chat=chat,
            message=message,
            author=user,
        )

        return message

    async def send_message(self, content):
        chat = await self.get_chat(content['chat'])
        user = self.scope['user']
        message = await self.register_chat_message(
            chat=chat,
            message=content['message'],
            user=user
        )
        serialized_message = serializers.ChatMessageSerializer(message)

        await self.send_json({'message': serialized_message.data})
