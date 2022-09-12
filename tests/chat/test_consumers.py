from channels.auth import AuthMiddlewareStack
from channels.db import database_sync_to_async
from channels.testing import WebsocketCommunicator
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TransactionTestCase
from model_bakery import baker

from chat.consumers import ChatConsumer
from common.tools.sync import async_manager_func
from tests.utils import fake

User = get_user_model()


class TestChatConsumer(TransactionTestCase):
    url = '/ws/chat/'

    def setUp(self):
        self.chat = baker.make_recipe('chat.chat')
        self.user = baker.make_recipe('registration.user')

    async def test_chat_consumer_connect_ok(self):
        consumer = WebsocketCommunicator(
            application=AuthMiddlewareStack(ChatConsumer.as_asgi()),
            path=self.url,
        )
        connected, _ = await consumer.connect()

        self.assertTrue(connected)

        await consumer.disconnect()

    async def test_anonymous_setup_channel_layer_ok(self):
        consumer = WebsocketCommunicator(
            application=AuthMiddlewareStack(ChatConsumer.as_asgi()),
            path=self.url,
        )
        await consumer.connect()
        await consumer.send_json_to({
            'type': 'setup_channel_layer',
            'chat': self.chat.pk,
        })
        response = await consumer.receive_json_from()

        self.assertEqual('info', response['type'])
        self.assertEqual('User not authenticated.', response['content']['message'])

        await consumer.disconnect()

    async def test_authenticated_setup_channel_layer_ok(self):
        consumer = WebsocketCommunicator(
            application=AuthMiddlewareStack(ChatConsumer.as_asgi()),
            path=self.url,
        )
        consumer.scope['user'] = self.user
        await consumer.connect()
        await consumer.send_json_to({
            'type': 'setup_channel_layer',
            'chat': self.chat.pk,
        })
        response = await consumer.receive_json_from()

        self.assertEqual('info', response['type'])
        self.assertEqual('Chat connected!', response['content']['message'])

        await consumer.disconnect()

    async def test_anonymous_send_message_ko(self):
        message = fake.sentence()
        consumer = WebsocketCommunicator(
            application=AuthMiddlewareStack(ChatConsumer.as_asgi()),
            path=self.url,
        )
        await consumer.connect()
        await consumer.send_json_to({
            'type': 'send_message',
            'chat': self.chat.pk,
            'message': message,
        })
        response = await consumer.receive_json_from()

        self.assertEqual('info', response['type'])
        self.assertEqual('User not authenticated.', response['content']['message'])

        await consumer.disconnect()

    async def test_anonymous_send_message_ok(self):
        message = fake.sentence()
        consumer = WebsocketCommunicator(
            application=AuthMiddlewareStack(ChatConsumer.as_asgi()),
            path=self.url,
        )
        consumer.scope['user'] = self.user
        await consumer.connect()
        await consumer.send_json_to({
            'type': 'setup_channel_layer',
            'chat': self.chat.pk,
        })
        await consumer.receive_from()
        await consumer.send_json_to({
            'type': 'send_message',
            'chat': self.chat.pk,
            'message': message,
        })
        response = await consumer.receive_json_from()

        self.assertEqual('send_message', response['type'])
        self.assertEqual(message, response['content']['message'])

        await consumer.disconnect()

    async def test_anonymous_make_roll_ko(self):
        consumer = WebsocketCommunicator(
            application=AuthMiddlewareStack(ChatConsumer.as_asgi()),
            path=self.url,
        )
        await consumer.connect()
        await consumer.send_json_to({
            'type': 'make_roll',
            'chat': self.chat.pk,
        })
        response = await consumer.receive_json_from()

        self.assertEqual('info', response['type'])
        self.assertEqual('User not authenticated.', response['content']['message'])

        await consumer.disconnect()

    async def test_authenticated_make_roll_ok(self):
        # NOTE: Seems like migration `registration.0008` is not applied or removed before test
        bot_user_exists = await async_manager_func(User, 'filter', email=settings.DEFAULT_FROM_EMAIL)
        bot_user_exists = await database_sync_to_async(bot_user_exists.exists)()
        if not bot_user_exists:
            await async_manager_func(
                model=User,
                func='create',
                username='Oil & Rope Bot',
                email=settings.DEFAULT_FROM_EMAIL,
                password='th1s1s4s3cur3',
            )

        consumer = WebsocketCommunicator(
            application=AuthMiddlewareStack(ChatConsumer.as_asgi()),
            path=self.url,
        )
        consumer.scope['user'] = self.user
        await consumer.connect()
        await consumer.send_json_to({
            'type': 'setup_channel_layer',
            'chat': self.chat.pk,
        })
        await consumer.receive_from()
        await consumer.send_json_to({
            'type': 'make_roll',
            'chat': self.chat.pk,
            'message': f'{settings.BOT_COMMAND_PREFIX}roll 1d20',
        })
        response = await consumer.receive_json_from()

        self.assertEqual('send_message', response['type'])
        self.assertIn('1d20', response['roll'])

        await consumer.disconnect()
