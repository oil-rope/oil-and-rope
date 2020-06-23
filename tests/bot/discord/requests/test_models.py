from django.conf import settings
from django.test import TestCase

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

    def test_loads_ok(self):
        attrs = self.response.json().keys()

        user_has_attrs = all([hasattr(self.user, att) for att in attrs])
        assert user_has_attrs

        all_attrs_are_correct = all([getattr(self.user, att) == self.response.json()[att] for att in attrs])
        assert all_attrs_are_correct

    def test_create_dm_ko(self):
        # A bot cannot create a channel with itself
        with self.assertRaises(DiscordApiException):
            self.user.create_dm()

    def test_create_dm_ok(self):
        user = self.api_class(316302647722377219)
        dm = user.create_dm()

        assert isinstance(dm, models.Channel)
