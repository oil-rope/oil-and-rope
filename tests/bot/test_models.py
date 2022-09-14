import unittest
from unittest.mock import MagicMock, patch

from django.test import TestCase, override_settings
from faker import Faker

from bot import models
from bot.exceptions import DiscordApiException, HelpfulError
from tests.mocks.discord import (create_dm_response, create_dm_to_user_unavailable_response, create_message,
                                 current_bot_response, user_response)
from tests.utils import fake

from ..utils import check_litecord_connection
from .helpers.constants import CHANNEL, LITECORD_API_URL, LITECORD_TOKEN


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

    @patch('bot.models.discord_api_get')
    def test_calls_discord_api_request_if_response_is_not_given_ok(self, mocker: MagicMock):
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
        with patch('bot.models.discord_api_get') as mocker_api_get:
            mocker_api_get.return_value = cls.user_response
            cls.user = cls.api_class(cls.identifier)

    @patch('bot.models.discord_api_get')
    def test_from_bot_ok(self, mocker: MagicMock):
        response = current_bot_response()
        mocker.return_value = response
        bot = self.api_class.from_bot()

        self.assertEqual(bot.id, response.json()['id'])

    @patch('bot.utils.discord_api_post')
    def test_create_dm_to_bot_ko(self, mocker_api_post: MagicMock):
        mocker_api_post.return_value = create_dm_to_user_unavailable_response()
        # A bot cannot create a message with itself
        with self.assertRaises(DiscordApiException):
            self.user.create_dm()

    @patch('bot.models.discord_api_post')
    def test_create_dm_to_user_in_same_server_ok(self, mocker_api_post: MagicMock):
        mocker_api_post.return_value = create_dm_response(recipients=[self.user_response.json()])

        dm = self.user.create_dm()

        self.assertTrue(isinstance(dm, models.Channel))

    def test_send_message_to_user_in_same_server_ok(self):
        dm_response = create_dm_response(recipients=[self.user_response.json()])
        channel_id = dm_response.json()['id']
        channel_mock = models.Channel(channel_id, response=dm_response)
        with patch.object(models.User, 'create_dm', return_value=channel_mock):
            msg_response = create_message(channel_id=channel_id)
            msg_id = msg_response.json()['id']
            msg_mock = models.Message(channel_mock, msg_id, response=msg_response)
            with patch.object(models.Channel, 'send_message', return_value=msg_mock):
                msg = self.user.send_message(fake.word())

        self.assertTrue(isinstance(msg, models.Message))

    def test_str_ok(self):
        expected_msg = f'{self.user.username} ({self.user.id})'

        # NOTE: We use `repr` since it shares method with `__str__`
        self.assertEqual(expected_msg, repr(self.user))


class TestChannel(TestCase):
    api_class = models.Channel

    def setUp(self):
        self.identifier = f'{fake.random_number(digits=18)}'
        user_res = user_response()
        with patch('bot.models.discord_api_get') as mock_user_response:
            mock_user_response.return_value = user_res
            self.user = models.User(self.identifier)

        with patch('bot.models.discord_api_get') as mock_channel_response:
            mock_channel_response.return_value = create_dm_response(id=self.identifier, recipients=[user_res.json()])
            self.dm = self.api_class(id=self.identifier)

    def test_send_message_ok(self):
        text = fake.paragraph()

        with patch('bot.models.discord_api_post') as mock_send_message:
            mock_send_message.return_value = create_message(content=text)
            msg = self.dm.send_message(text)

        self.assertTrue(isinstance(msg, models.Message))
        self.assertEqual(text, msg.content)

    @unittest.skipIf(not check_litecord_connection(), 'Litecord seems to be unreachable.')
    def test_str_without_name_ok(self):
        expected = f'Channel {self.dm.channel_type.name} ({self.dm.id})'
        result = repr(self.dm)

        self.assertEqual(expected, result)

    @unittest.skipIf(not check_litecord_connection(), 'Litecord seems to be unreachable.')
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
