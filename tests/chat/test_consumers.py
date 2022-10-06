from channels.auth import AuthMiddlewareStack
from channels.testing import WebsocketCommunicator
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TransactionTestCase
from model_bakery import baker
from rest_framework.authtoken.models import Token

from chat.consumers import ChatConsumer
from tests.utils import fake

User = get_user_model()


class TestChatConsumer(TransactionTestCase):
    url = '/ws/chat/'

    def setUp(self):
        self.chat = baker.make_recipe('chat.chat')
        self.user = baker.make_recipe('registration.user')
        self.bot, self.bot_created = User.objects.get_or_create(
            username='Oil & Rope Bot',
            email=settings.DEFAULT_FROM_EMAIL,
            defaults={
                'password': 'th1s1s4s3cur3',
            },
        )
        self.user_token = Token.objects.create(user=self.user).key

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

        self.assertEqual('group_send_message', response['type'])
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

        self.assertEqual('group_send_message', response['type'])
        self.assertIn('1d20', response['roll'])

        await consumer.disconnect()

    async def test_authenticated_make_roll_incorrect_syntax_ok(self):
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
            'message': f'{settings.BOT_COMMAND_PREFIX}roll XdY',
        })
        response = await consumer.receive_json_from()

        self.assertEqual('group_send_message', response['type'])
        self.assertEqual('Dice roll `xdy` syntax is incorrect.', response['content']['message'])
        self.assertDictEqual({}, response['roll'])

        await consumer.disconnect()

    async def test_non_authenticated_with_token_setup_channel_ok(self):
        consumer = WebsocketCommunicator(
            application=AuthMiddlewareStack(ChatConsumer.as_asgi()),
            path=self.url,
        )
        await consumer.connect()
        await consumer.send_json_to({
            'type': 'setup_channel_layer',
            'chat': self.chat.pk,
            'token': self.user_token,
        })
        response = await consumer.receive_json_from()

        self.assertEqual('info', response['type'])
        self.assertEqual('Chat connected!', response['content']['message'])

    async def test_non_authenticated_with_false_token_setup_channel_ko(self):
        consumer = WebsocketCommunicator(
            application=AuthMiddlewareStack(ChatConsumer.as_asgi()),
            path=self.url,
        )
        await consumer.connect()
        await consumer.send_json_to({
            'type': 'setup_channel_layer',
            'chat': self.chat.pk,
            'token': fake.sentence(),
        })
        response = await consumer.receive_json_from()

        self.assertEqual('info', response['type'])
        self.assertEqual('User not authenticated.', response['content']['message'])
