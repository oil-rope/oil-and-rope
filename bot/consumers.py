import json

from channels.generic.websocket import AsyncWebsocketConsumer

from .models import DiscordUser


class BotConnectionOnRegisterConsumer(AsyncWebsocketConsumer):
    """
    WebSocket for Bot Actions.
    """

    async def connect(self):
        super(BotConnectionOnRegisterConsumer, self).connect()

    async def receive(self, text_data=None, bytes_data=None):
        discord_id = int(text_data)
        data = {
            'exists': False
        }
        if DiscordUser.objects.filter(pk=discord_id).exists():
            # Discord User exists
            data['exists'] = True
            await self.send(json.dumps(data))
        else:
            await self.send(json.dumps(data))
