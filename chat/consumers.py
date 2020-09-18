from core.consumers import HandlerJsonWebsocketConsumer


class ChatConsumer(HandlerJsonWebsocketConsumer):

    async def connect(self):
        await super().connect()

    async def send_message(self, content):
        await self.send_json({'content': content})
