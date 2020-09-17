from core.consumers import HandlerJsonWebsocketConsumer


class ChatConsumer(HandlerJsonWebsocketConsumer):

    async def connect(self):
        await super().connect()

    async def get_user(self, content):
        await self.send_json({'content': True})
        pass
