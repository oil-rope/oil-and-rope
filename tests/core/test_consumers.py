import pytest
from channels.testing import WebsocketCommunicator

from api.serializers.common import WebSocketMessageSerializer
from core.consumers import HandlerJsonWebsocketConsumer
from tests.utils import fake


class TestTypedConsumerMixin:
    @pytest.mark.asyncio
    async def test_websocket_handler_not_given_serializer_class_ko(self):
        class ConsumerClass(HandlerJsonWebsocketConsumer):
            pass

        communicator = WebsocketCommunicator(ConsumerClass.as_asgi(), '/ws/test/')
        data = {
            'type': fake.word()
        }
        await communicator.send_json_to(data)

        with pytest.raises(NotImplementedError):
            await communicator.receive_json_from()


class TestHandlerJsonWebsocketConsumer:
    @pytest.fixture(scope='class')
    def consumer(self):
        class ConsumerClass(HandlerJsonWebsocketConsumer):
            serializer_class = WebSocketMessageSerializer

            async def test(self, content):
                return await self.send_json(content)

        return ConsumerClass

    @pytest.mark.asyncio
    async def test_websocket_sends_error(self, consumer):
        communicator = WebsocketCommunicator(consumer.as_asgi(), '/ws/test/')
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

    @pytest.mark.asyncio
    async def test_websocket_handler_non_existent_function(self, consumer):
        communicator = WebsocketCommunicator(consumer.as_asgi(), '/ws/test/')
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

    @pytest.mark.asyncio
    async def test_websocket_handler_existent_function(self, consumer):
        communicator = WebsocketCommunicator(consumer.as_asgi(), '/ws/test/')
        message = fake.word()
        data = {
            'type': 'test',
            'content': {'message': message},
        }
        await communicator.send_json_to(data)
        response = await communicator.receive_json_from()

        assert response == {'content': {'message': message}}
