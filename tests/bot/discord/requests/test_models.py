import os

from django.conf import settings
from django.test import TestCase
from faker import Faker

from bot.discord.requests import models
from bot.discord.requests.utils import discord_api_get
from bot.exceptions import DiscordApiException

LITECORD_API_URL = os.getenv('LITECORD_API_URL', 'http://litecord.oilandrope-project.com/api/v6/')
LITECORD_TOKEN = os.getenv('LITECORD_TOKEN', 'NzI1MzI2ODM1MzA2NTk4NDAw.XvNHrw.Wpd_yAh7aVWaOC9VyTeATIGpYmU')
DUMMY_USER_WITH_SAME_SERVER = 725326487963701248
DUMMY_USER_WITH_DIFFERENT_SERVER = 725374189317525504


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

    def test_create_dm_ok(self):
        with self.settings(DISCORD_API_URL=LITECORD_API_URL, BOT_TOKEN=LITECORD_TOKEN):
            user = self.api_class(DUMMY_USER_WITH_SAME_SERVER)
            dm = user.create_dm()

            self.assertTrue(isinstance(dm, models.Channel))

    def test_send_message_ok(self):
        with self.settings(DISCORD_API_URL=LITECORD_API_URL, BOT_TOKEN=LITECORD_TOKEN):
            user = self.api_class(DUMMY_USER_WITH_SAME_SERVER)
            msg = user.send_message(self.faker.word())

            self.assertTrue(isinstance(msg, models.Message))

    def test_send_message_ko(self):
        with self.settings(DISCORD_API_URL=LITECORD_API_URL, BOT_TOKEN=LITECORD_TOKEN):
            user = self.api_class(DUMMY_USER_WITH_DIFFERENT_SERVER)

            with self.assertRaises(DiscordApiException):
                user.send_message(self.faker.word())

    def test_str_ok(self):
        user = self.api_class(self.id)
        expected = f'{user.username} ({user.id})'
        result = repr(user)

        self.assertEqual(expected, result)
