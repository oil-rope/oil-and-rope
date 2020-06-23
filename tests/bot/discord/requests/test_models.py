from django.conf import settings
from django.test import TestCase
from faker import Faker

from bot.discord.requests import models
from bot.discord.requests.utils import discord_api_get
from bot.exceptions import DiscordApiException


class TestUser(TestCase):
    api_class = models.User

    def setUp(self):
        # We attack Bot's ID
        url = f'{settings.DISCORD_API_URL}users/@me'
        response = discord_api_get(url)

        self.id = response.json()['id']
        self.url = f'{self.api_class.base_url}{self.id}'
        self.response = discord_api_get(self.url)
        self.user = self.api_class(self.id)

        self.faker = Faker()

    def test_loads_ok(self):
        attrs = self.response.json().keys()

        user_has_attrs = all([hasattr(self.user, att) for att in attrs])
        self.assertTrue(user_has_attrs)

        all_attrs_are_correct = all([getattr(self.user, att) == self.response.json()[att] for att in attrs])
        self.assertTrue(all_attrs_are_correct)

    def test_loads_from_response_ok(self):
        user = self.api_class(self.id, response=self.response)
        attrs = self.response.json().keys()

        user_has_attrs = all([hasattr(user, att) for att in attrs])
        self.assertTrue(user_has_attrs)

        all_attrs_are_correct = all([getattr(user, att) == self.response.json()[att] for att in attrs])
        self.assertTrue(all_attrs_are_correct)

    def test_loads_from_bot_ok(self):
        bot = self.api_class.from_bot()
        self.assertEqual(self.user.id, bot.id)

    def test_create_dm_ko(self):
        # A bot cannot create a channel with itself
        with self.assertRaises(DiscordApiException):
            self.user.create_dm()

    def test_create_dm_ok(self):
        user = self.api_class(316302647722377219)
        dm = user.create_dm()

        self.assertTrue(isinstance(dm, models.Channel))

    def test_send_message_ok(self):
        user = self.api_class(316302647722377219)
        msg = user.send_message(self.faker.word())

        self.assertTrue(isinstance(msg, models.Message))

    def test_str_ok(self):
        expected = f'{self.user.username} ({self.user.id})'
        result = repr(self.user)

        self.assertEqual(expected, result)
