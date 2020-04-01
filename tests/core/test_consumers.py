import pytest
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from django.urls import path
from django.utils.translation import ugettext_lazy as _

from core.consumers import HandlerJsonWebsocketConsumer

application = URLRouter([
    path('testws/', WebsocketCommunicator),
])


@pytest.mark.asyncio
async def test_websocket_sends_error():
    communicator = WebsocketCommunicator(HandlerJsonWebsocketConsumer, 'testws/')
    data = {
        'dump': 'dump'
    }
    error_response = {
        'error': _('No type given') + '.'
    }
    await communicator.send_json_to(data)
    response = await communicator.receive_json_from()
    assert response == error_response, 'Incorrect response.'

    # Disconnect WebSocket to avoid pending tasks
    await communicator.disconnect()
