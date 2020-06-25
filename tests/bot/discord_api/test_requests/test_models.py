from django.conf import settings
from django.test import TestCase, override_settings
from faker import Faker

from bot.discord_api import models
from bot.discord_api.utils import discord_api_get
from bot.exceptions import DiscordApiException, HelpfulError

from ...helpers.constants import (CHANNEL, LITECORD_API_URL, LITECORD_TOKEN, USER_WITH_DIFFERENT_SERVER,
                                  USER_WITH_SAME_SERVER)


class TestApiMixin(TestCase):

    def test_raises_error_with_empty_url_ko(self):
        with self.assertRaises(HelpfulError):
            models.ApiMixin()


class TestUser(TestCase):
    api_class = models.User

    def setUp(self):
        # We attack Bot's ID
        url = f'{settings.DISCORD_API_URL}users/@me'
        response = discord_api_get(url)
        self.id = response.json()['id']
        self.id = int(self.id)

        self.faker = Faker()

    def test_from_bot_ok(self):
        user = self.api_class.from_bot()

        self.assertEqual(user.id, self.id)

    def test_create_dm_ko(self):
        user = self.api_class(self.id)

        # A bot cannot create a message with itself
        with self.assertRaises(DiscordApiException):
            user.create_dm()

    @override_settings(DISCORD_API_URL=LITECORD_API_URL, BOT_TOKEN=LITECORD_TOKEN)
    def test_create_dm_ok(self):
        user = self.api_class(USER_WITH_SAME_SERVER)
        dm = user.create_dm()

        self.assertTrue(isinstance(dm, models.Channel))

    @override_settings(DISCORD_API_URL=LITECORD_API_URL, BOT_TOKEN=LITECORD_TOKEN)
    def test_send_message_ok(self):
        user = self.api_class(USER_WITH_SAME_SERVER)
        msg = user.send_message(self.faker.word())

        self.assertTrue(isinstance(msg, models.Message))

    @override_settings(DISCORD_API_URL=LITECORD_API_URL, BOT_TOKEN=LITECORD_TOKEN)
    def test_send_message_ko(self):
        user = self.api_class(USER_WITH_DIFFERENT_SERVER)

        with self.assertRaises(DiscordApiException):
            user.send_message(self.faker.word())

    def test_str_ok(self):
        user = self.api_class(self.id)
        expected = f'{user.username} ({user.id})'
        result = repr(user)

        self.assertEqual(expected, result)


@override_settings(DISCORD_API_URL=LITECORD_API_URL, BOT_TOKEN=LITECORD_TOKEN)
class TestChannel(TestCase):
    api_class = models.Channel

    def setUp(self):
        self.faker = Faker()

        user = models.User(USER_WITH_SAME_SERVER)
        self.channel = user.create_dm()

    def test_loads_ok(self):
        channel_has_attrs = all([hasattr(self.channel, attr)] for attr in self.channel.json_response.keys())

        self.assertTrue(channel_has_attrs)

    def test_loads_from_response_ok(self):
        channel = self.api_class(self.id, response=self.channel.response)
        channel_has_attrs = all([hasattr(channel, attr)] for attr in channel.json_response.keys())

        self.assertTrue(channel_has_attrs)

    def test_send_message_ok(self):
        text = self.faker.paragraph()
        msg = self.channel.send_message(text)

        self.assertTrue(isinstance(msg, models.Message))
        self.assertEqual(text, msg.content)

    def test_str_without_name_ok(self):
        expected = f'Channel {self.channel.type.name} ({self.channel.id})'
        result = repr(self.channel)

        self.assertEqual(expected, result)

    def test_str_with_name_ok(self):
        channel = self.api_class(CHANNEL)
        expected = f'Channel {channel.name} ({channel.id})'
        result = repr(channel)

        self.assertEqual(expected, result)


@override_settings(DISCORD_API_URL=LITECORD_API_URL, BOT_TOKEN=LITECORD_TOKEN)
class TestMessage(TestCase):
    api_class = models.Message

    def setUp(self):
        self.faker = Faker()
        self.channel = models.Channel(CHANNEL)
        self.text = self.faker.paragraph()
        self.message = self.channel.send_message(self.text)

    def test_loads_ok(self):
        message_has_attrs = all([hasattr(self.message, attr)] for attr in self.message.json_response.keys())

        self.assertTrue(message_has_attrs)

    def test_loads_from_given_channel_id_ok(self):
        message = self.api_class(self.channel.id, self.message.id)
        message_has_attrs = all([hasattr(message, attr)] for attr in message.json_response.keys())

        self.assertTrue(message_has_attrs)

    def test_edit_ok(self):
        text = self.faker.paragraph()
        msg = self.message.edit(text)

        self.assertEqual(text, msg.content)
        # Message still the same
        self.assertEqual(self.message.id, msg.id)

    def test_str_ok(self):
        expected = f'({self.message.id}): {self.message.content}'
        result = repr(self.message)

        self.assertEqual(expected, result)
