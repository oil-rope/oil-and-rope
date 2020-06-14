import faker
import pytest
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from django.urls import path
from django.utils.translation import gettext_lazy as _

from core.consumers import HandlerJsonWebsocketConsumer

application = URLRouter([
    path('testws/', WebsocketCommunicator),
])

fake = faker.Faker()


@pytest.mark.asyncio
async def test_websocket_sends_error():
    communicator = WebsocketCommunicator(HandlerJsonWebsocketConsumer, 'testws/')
    data = {
        'dump': fake.word()
    }
    await communicator.send_json_to(data)

    error_response = {
        'error': _('No type given') + '.'
    }
    response = await communicator.receive_json_from()
    assert response == error_response, 'Incorrect response.'

    # Disconnect WebSocket to avoid pending tasks
    await communicator.disconnect()


@pytest.mark.asyncio
async def test_websocket_handler_non_existent_function():
    communicator = WebsocketCommunicator(HandlerJsonWebsocketConsumer, 'testws/')
    data = {
        'type': fake.word()
    }
    await communicator.send_json_to(data)
    response = await communicator.receive_json_from()

    error_response = {
        'error': _('Non existent type') + '.'
    }
    assert response == error_response, 'Incorrect response.'

    # Disconnect WebSocket to avoid pending tasks
    await communicator.disconnect()
