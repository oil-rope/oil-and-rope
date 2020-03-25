from channels.generic.websocket import AsyncJsonWebsocketConsumer

from .models import DiscordUser


class BotConnectionOnRegisterConsumer(AsyncJsonWebsocketConsumer):
    """
    WebSocket for Bot Actions.
    """

    async def connect(self):
        await super(BotConnectionOnRegisterConsumer, self).connect()

    async def receive_json(self, content, **kwargs):
        discord_id = content['discord_id']
        data = {
            'exists': False
        }
        if DiscordUser.objects.filter(pk=discord_id).exists():
            # Discord User exists
            data['exists'] = True
            await self.send_json(data)
        else:
            await self.send_json(data)
