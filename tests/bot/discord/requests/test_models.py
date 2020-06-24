from django.conf import settings
from django.test import TestCase, override_settings
from faker import Faker

from bot.discord.requests import models
from bot.discord.requests.utils import discord_api_get
from bot.exceptions import DiscordApiException
from tests.bot.helpers.constants import (DUMMY_USER_WITH_DIFFERENT_SERVER, DUMMY_USER_WITH_SAME_SERVER,
                                         LITECORD_API_URL, LITECORD_TOKEN)


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
        user = self.api_class(DUMMY_USER_WITH_SAME_SERVER)
        dm = user.create_dm()

        self.assertTrue(isinstance(dm, models.Channel))

    @override_settings(DISCORD_API_URL=LITECORD_API_URL, BOT_TOKEN=LITECORD_TOKEN)
    def test_send_message_ok(self):
        user = self.api_class(DUMMY_USER_WITH_SAME_SERVER)
        msg = user.send_message(self.faker.word())

        self.assertTrue(isinstance(msg, models.Message))

    @override_settings(DISCORD_API_URL=LITECORD_API_URL, BOT_TOKEN=LITECORD_TOKEN)
    def test_send_message_ko(self):
        user = self.api_class(DUMMY_USER_WITH_DIFFERENT_SERVER)

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
        user = models.User(DUMMY_USER_WITH_SAME_SERVER)
        self.channel = user.create_dm()

    def test_loads_ok(self):
        channel_has_attrs = all([hasattr(self.channel, attr)] for attr in self.channel.json_response.keys())

        self.assertTrue(channel_has_attrs)

    def test_loads_from_response_ok(self):
        channel = self.api_class(self.id, response=self.channel.response)
        channel_has_attrs = all([hasattr(channel, attr)] for attr in channel.json_response.keys())

        self.assertTrue(channel_has_attrs)
