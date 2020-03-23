import functools
import json

from channels.generic.websocket import AsyncWebsocketConsumer

from .models import DiscordUser


def proccess_json():
    """
    Gets `text_data` and transforms it into a :class:`dict` for sugar syntax.
    """

    def wrapper(func):
        @functools.wraps(func)
        async def wrapped(*args, **kwargs):
            kwargs['text_data'] = json.loads(kwargs['text_data'])
            return await func(*args, **kwargs)
        return wrapped
    return wrapper


class BotConnectionOnRegisterConsumer(AsyncWebsocketConsumer):
    """
    WebSocket for Bot Actions.
    """

    async def connect(self):
        await super(BotConnectionOnRegisterConsumer, self).connect()

    @proccess_json()
    async def receive(self, text_data=None, bytes_data=None):
        discord_id = text_data['discord_id']
        data = {
            'exists': False
        }
        if DiscordUser.objects.filter(pk=discord_id).exists():
            # Discord User exists
            data['exists'] = True
            await self.send(json.dumps(data))
        else:
            await self.send(json.dumps(data))
