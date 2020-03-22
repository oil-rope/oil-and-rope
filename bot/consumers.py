from channels.generic.websocket import AsyncWebsocketConsumer


class BotConsumer(AsyncWebsocketConsumer):
    """
    WebSocket for Bot Actions.
    """

    async def receive(self, text_data=None, bytes_data=None):
        pass
