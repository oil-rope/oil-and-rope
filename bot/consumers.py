from channels.db import database_sync_to_async

from core.consumers import HandlerJsonWebsocketConsumer

from .models import DiscordUser


class BotConsumer(HandlerJsonWebsocketConsumer):
    """
    WebSocket for Bot Actions.
    """

    async def connect(self):
        await super().connect()

    @database_sync_to_async
    def get_user(self, discord_id):
        discord_user = DiscordUser.objects.get(id=discord_id)
        return discord_user

    async def check_user(self, content):
        discord_id = content.get('discord_id', None)
        try:
            await self.get_user(discord_id)
            exists = True
        except DiscordUser.DoesNotExist:
            exists = False
        content = {'exists': exists}
        await self.send_json(content)
