import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.utils.translation import gettext_lazy as _

from common.enums import WebSocketCloseCodes


class TypedConsumerMixin:
    """
    This mixin checks for received data and checks that all required fields are present.

    Parameters
    ----------
    serializer_class: :class:`rest_framework.serializers.Serializer`
        The serializer class used to validate the data.

    Methods
    -------
    get_serializer(data):
        Returns the serializer instance.
    check_data(serializer):
        Checks that the data is valid using serializer's `is_valid` method.
        Returns True if the data is valid, False otherwise.
    """

    serializer_class = None

    def get_serializer(self, data, serializer_class=None):
        """
        Returns the serializer instance.
        """

        if serializer_class:
            return serializer_class(data=data)
        if not self.serializer_class:
            raise NotImplementedError('You must either define `serializer_class` or override `get_serializer`.')
        return self.serializer_class(data=data)

    async def check_data(self, serializer):
        """
        Checks that the data is valid using serializer's `is_valid` method.
        """

        return await sync_to_async(serializer.is_valid)()

    async def receive(self, text_data=None, bytes_data=None, **kwargs):
        if text_data:
            data = json.loads(text_data)
            serializer = self.get_serializer(data)
            check = await self.check_data(serializer)
            if not check:
                await self.send_json({
                    'type': 'error',
                    'content': {
                        'message': _('invalid data').capitalize(),
                    },
                })
                await super().close(code=WebSocketCloseCodes.INVALID_FRAME_PAYLOAD_DATA.value)
            else:
                await super().receive(text_data, bytes_data, **kwargs)
        else:
            await super().receive(text_data, bytes_data, **kwargs)


class HandlerJsonWebsocketConsumer(TypedConsumerMixin, AsyncJsonWebsocketConsumer):
    """
    This consumer will get a `type` parameter within a JSON and call the function.
    If function does not exists returns error.
    If type is not given returns error message.
    """

    async def handler(self, content):
        func = content['type']
        if not hasattr(self, func):
            content = {
                'type': 'error',
                'content': {'message': _('given type does not exist.').capitalize()},
            }
            await super().send_json(content)
            await super().close(code=WebSocketCloseCodes.INVALID_FRAME_PAYLOAD_DATA.value)
        else:
            func = getattr(self, func)
            del content['type']
            await func(content)

    async def receive_json(self, content, **kwargs):
        # NOTE: We don't call `super().receive_json` because it's just a pass function.
        await self.handler(content, **kwargs)
