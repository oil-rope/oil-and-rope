import asyncio

from channels.testing import WebsocketCommunicator
from django.apps import apps
from django.shortcuts import reverse
from django.test import TestCase, override_settings
from model_bakery import baker
from rest_framework.authtoken.models import Token

from chat.consumers import ChatConsumer
from common.constants import models
from common.utils import create_faker

User = apps.get_model(models.USER_MODEL)

fake = create_faker()


class TestChatConsumer(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('chat:index')
        cls.user = baker.make_recipe('registration.user')
        cls.chat = baker.make_recipe('chat.chat')
        cls.token = Token.objects.create(user=cls.user).key

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
            'chat': self.chat.pk,
            'token': self.token,
        }
        await communicator.send_json_to(data)
        response = await communicator.receive_json_from()

        await communicator.disconnect()

        self.assertEqual('info', response['type'])
        self.assertEqual('ok', response['status'])
        self.assertEqual('Chat connected!', response['content'])

    @override_settings(CHANNEL_LAYERS={
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                'hosts': [('google.com', 6379)],
            },
        },
    })
    async def test_setup_channel_layer_ko(self):
        communicator = WebsocketCommunicator(ChatConsumer.as_asgi(), self.url)
        connected, protocol = await communicator.connect()

        self.assertTrue(connected, 'WebSocket doesn\'t connect')

        data = {
            'type': 'setup_channel_layer',
            'chat': self.chat.pk,
            'token': self.token,
        }
        await communicator.send_json_to(data)
        with self.assertRaises(asyncio.exceptions.TimeoutError):
            await communicator.receive_json_from()

        await communicator.disconnect()

    async def test_send_message_ok(self):
        communicator = WebsocketCommunicator(ChatConsumer.as_asgi(), self.url)
        connected, protocol = await communicator.connect()

        self.assertTrue(connected, 'WebSocket doesn\'t connect')

        data = {
            'type': 'setup_channel_layer',
            'chat': self.chat.pk,
            'token': self.token,
        }
        await communicator.send_json_to(data)
        await communicator.receive_from()

        msg = fake.word()
        data = {
            'type': 'send_message',
            'chat': self.chat.pk,
            'message': msg,
        }
        await communicator.send_json_to(data)
        response = await communicator.receive_json_from()

        self.assertEqual(response['type'], 'send_message')
        self.assertEqual(response['status'], 'ok')
        self.assertEqual(response['content'], msg)
