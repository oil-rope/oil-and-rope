from channels.testing import WebsocketCommunicator
from django.shortcuts import reverse
from django.test import TestCase
from model_bakery import baker

from chat.consumers import ChatConsumer
from common.utils import create_faker

fake = create_faker()


class TestChatConsumer(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('chat:index')
        cls.user = baker.make_recipe('registration.user')
        cls.chat = baker.make_recipe('chat.chat')

    async def test_connect_ok(self):
        communicator = WebsocketCommunicator(ChatConsumer.as_asgi(), self.url)
        connected, protocol = await communicator.connect()

        self.assertTrue(connected, 'WebSocket doesn\'t connect')

        await communicator.disconnect()

    async def test_setup_channel_layer_ok(self):
        communicator = WebsocketCommunicator(ChatConsumer.as_asgi(), self.url)
        connected, protocol = await communicator.connect()

        self.assertTrue(connected, 'WebSocket doesn\'t connect')

        data = {
            'type': 'setup_channel_layer',
            'chat': self.chat.pk
        }
        await communicator.send_json_to(data)
        await communicator.receive_json_from()

        await communicator.disconnect()
