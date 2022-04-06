import pytest
from channels.testing import WebsocketCommunicator

from api.serializers.common import WebSocketMessageSerializer
from core.consumers import HandlerJsonWebsocketConsumer
from tests import fake


@pytest.fixture(scope='function')
def consumer():
    class ConsumerClass(HandlerJsonWebsocketConsumer):
        serializer_class = WebSocketMessageSerializer
    return ConsumerClass


@pytest.mark.asyncio
async def test_websocket_sends_error(consumer):
    communicator = WebsocketCommunicator(consumer.as_asgi(), 'testws/')
    data = {
        'dump': fake.word()
    }
    await communicator.send_json_to(data)

    error_response = {
        'type': 'error',
        'content': {'message': 'Invalid data'},
    }
    response = await communicator.receive_json_from()
    assert response == error_response

    # Disconnect WebSocket to avoid pending tasks
    await communicator.disconnect()


@pytest.mark.asyncio
async def test_websocket_handler_non_existent_function(consumer):
    communicator = WebsocketCommunicator(consumer.as_asgi(), 'testws/')
    data = {
        'type': fake.word()
    }
    await communicator.send_json_to(data)
    response = await communicator.receive_json_from()

    error_response = {
        'type': 'error',
        'content': {'message': 'Given type does not exist.'},
    }
    assert response == error_response

    # Disconnect WebSocket to avoid pending tasks
    await communicator.disconnect()
