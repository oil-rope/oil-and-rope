from core.consumers import HandlerJsonWebsocketConsumer

from .models import DiscordUser


class BotConsumer(HandlerJsonWebsocketConsumer):
    """
    WebSocket for Bot Actions.
    """

    async def connect(self):
        await super().connect()

    async def check_user(self, content):
        discord_id = content.get('discord_id', None)
        exists = DiscordUser.objects.filter(id=discord_id).exists()
        content = {'exists': exists}
        await self.send_json(content)
