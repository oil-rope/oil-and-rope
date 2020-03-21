from unittest import mock

import discord
from django.test import TestCase
from faker import Faker

from bot import utils


class TestUtils(TestCase):

    def setUp(self):
        self.faker = Faker()
        guild_data = {
            'id': 1,
            'name': 'guild',
            'region': 'Europe',
            'verification_level': 2,
            'default_notications': 1,
            'afk_timeout': 100,
            'icon': 'icon.png',
            'banner': 'banner.png',
            'mfa_level': 1,
            'splash': 'splash.png',
            'system_channel_id': 464033278631084042,
            'description': 'mocking is fun',
            'max_presences': 10_000,
            'max_members': 100_000,
            'preferred_locale': 'UTC',
            'owner_id': 1,
            'afk_channel_id': 464033278631084042,
        }
        self.guild = discord.Guild(data=guild_data, state=mock.MagicMock())
        member_data = {
            'user': self.faker.word(),
            'roles': [self.faker.random_int(0, 10)],
            'created_at': self.faker.date_time()
        }
        self.member = discord.Member(data=member_data, guild=self.guild, state=self.guild._state)

    def test_nothing(self):
        discord_user = utils.get_or_create_discord_user(self.member)
        self.assertEqual(discord_user.id, self.member.id, 'User\'s ID does not match.')
