from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.utils.translation import ugettext_lazy as _


class HandlerJsonWebsocketConsumer(AsyncJsonWebsocketConsumer):
    """
    This consumer will get a `type` parameter within a JSON and call the function.
    If function does not exists returns error.
    If type is not given returns error message.
    """

    async def handler(self, content):
        func = content['type']
        if not hasattr(self, func):
            content = {
                'error': _('Inexistent type') + '.'
            }
            await super().send_json(content, True)
        else:
            func = getattr(self, func)
            del content['type']
            await func(content)

    async def receive_json(self, content, **kwargs):
        if 'type' not in content:
            content = {
                'error': _('No type given') + '.'
            }
            await super().send_json(content, True)
        else:
            await self.handler(content)
