import unittest
from unittest import mock

from django.test import TestCase, override_settings
from faker import Faker

from bot import models
from bot.exceptions import DiscordApiException, HelpfulError
from tests.utils import fake
from tests.mocks.discord import (create_dm_response, create_dm_to_user_unavailable_response, create_message,
                                 current_bot_response, user_response)

from ..utils import check_litecord_connection
from .helpers.constants import CHANNEL, LITECORD_API_URL, LITECORD_TOKEN, USER_WITH_SAME_SERVER


class TestApiMixin(TestCase):
    def test_raises_error_with_empty_url_ko(self):
        with self.assertRaises(HelpfulError):
            models.ApiMixin()

    def test_uses_response_if_given_ok(self):
        url = f'https://{fake.domain_name()}'
        fake_id = fake.random_number()
        response = user_response(id=fake_id)
        model_instance = models.ApiMixin(url=url, response=response)

        self.assertEqual(fake_id, model_instance.id)

    @mock.patch('bot.models.discord_api_get')
    def test_calls_discord_api_request_if_response_is_not_given_ok(self, mocker: mock.MagicMock):
        url = f'https://{fake.domain_name()}'
        fake_id = fake.random_number()
        mocker.return_value = user_response(id=fake_id)
        model_instance = models.ApiMixin(url=url)

        self.assertEqual(fake_id, model_instance.id)


class TestUser(TestCase):
    api_class = models.User

    @classmethod
    def setUpTestData(cls) -> None:
        cls.identifier = f'{fake.random_number(digits=18)}'
        cls.user_response = user_response(id=cls.identifier)
        with mock.patch('bot.models.discord_api_get') as mocker_get:
            mocker_get.return_value = cls.user_response
            cls.user = cls.api_class(cls.identifier)

    @mock.patch('bot.models.discord_api_get')
    def test_from_bot_ok(self, mocker: mock.MagicMock):
        response = current_bot_response()
        mocker.return_value = response
        bot = self.api_class.from_bot()

        self.assertEqual(bot.id, response.json()['id'])

    @mock.patch('bot.utils.discord_api_request')
    def test_create_dm_to_bot_ko(self, mocker_request: mock.MagicMock):
        mocker_request.return_value = create_dm_to_user_unavailable_response()
        # A bot cannot create a message with itself
        with self.assertRaises(DiscordApiException):
            self.user.create_dm()

    @mock.patch('bot.models.discord_api_post')
    def test_create_dm_to_user_in_same_server_ok(self, mocker_post: mock.MagicMock):
        mocker_post.return_value = create_dm_response(recipients=[self.user_response.json()])

        dm = self.user.create_dm()

        self.assertTrue(isinstance(dm, models.Channel))

    @mock.patch('bot.models.discord_api_post')
    @mock.patch('bot.models.discord_api_get')
    def test_send_message_to_user_in_same_server_ok(self, mocker_get: mock.MagicMock, mocker_post: mock.MagicMock):
        dm_response = create_dm_response(recipients=[self.user_response.json()])
        mocker_get.return_value = dm_response
        mocker_post.return_value = dm_response

        with mock.patch('bot.models.Channel.send_message') as mocker_msg:
            channel_id = dm_response.json()['id']
            msg_response = create_message(channel_id=channel_id)
            mocker_msg.return_value = models.Message(channel_id, msg_response.json()['id'], response=msg_response)

            msg = self.user.send_message(fake.word())

        self.assertTrue(isinstance(msg, models.Message))

    @unittest.skipIf(not check_litecord_connection(), 'Litecord seems to be unreachable.')
    def test_send_message_to_user_in_different_server_ko(self):
        with self.assertRaises(DiscordApiException):
            self.user.send_message(fake.word())


@unittest.skipIf(not check_litecord_connection(), 'Litecord seems to be unreachable.')
@override_settings(DISCORD_API_URL=LITECORD_API_URL, BOT_TOKEN=LITECORD_TOKEN)
class TestChannel(TestCase):
    api_class = models.Channel

    def setUp(self):
        self.faker = Faker()

        user = models.User(USER_WITH_SAME_SERVER)
        self.channel = user.create_dm()

    def test_loads_ok(self):
        channel_has_attrs = all([hasattr(self.channel, attr)] for attr in self.channel.json.keys())

        self.assertTrue(channel_has_attrs)

    def test_loads_from_response_ok(self):
        channel = self.api_class(self.id, response=self.channel.response)
        channel_has_attrs = all([hasattr(channel, attr)] for attr in channel.json.keys())

        self.assertTrue(channel_has_attrs)

    def test_send_message_ok(self):
        text = self.faker.paragraph()
        msg = self.channel.send_message(text)

        self.assertTrue(isinstance(msg, models.Message))
        self.assertEqual(text, msg.content)

    def test_str_without_name_ok(self):
        expected = f'Channel {self.channel.channel_type.name} ({self.channel.id})'
        result = repr(self.channel)

        self.assertEqual(expected, result)

    def test_str_with_name_ok(self):
        channel = self.api_class(CHANNEL)
        expected = f'Channel {channel.name} ({channel.id})'
        result = repr(channel)

        self.assertEqual(expected, result)


@unittest.skipIf(not check_litecord_connection(), 'Litecord seems to be unreachable.')
@override_settings(DISCORD_API_URL=LITECORD_API_URL, BOT_TOKEN=LITECORD_TOKEN)
class TestMessage(TestCase):
    api_class = models.Message

    def setUp(self):
        self.faker = Faker()
        self.channel = models.Channel(CHANNEL)
        self.text = self.faker.paragraph()
        self.message = self.channel.send_message(self.text)

    def test_loads_ok(self):
        message_has_attrs = all([hasattr(self.message, attr)] for attr in self.message.json.keys())

        self.assertTrue(message_has_attrs)

    def test_loads_from_given_channel_id_ok(self):
        message = self.api_class(self.channel.id, self.message.id)
        message_has_attrs = all([hasattr(message, attr)] for attr in message.json.keys())

        self.assertTrue(message_has_attrs)

    def test_edit_ok(self):
        text = self.faker.paragraph()
        msg = self.message.edit(text)

        self.assertEqual(text, msg.content)
        # Check if message is the same
        self.assertEqual(self.message.id, msg.id)

    def test_str_ok(self):
        expected = f'({self.message.id}): {self.message.content}'
        result = repr(self.message)

        self.assertEqual(expected, result)
