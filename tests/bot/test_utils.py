import unittest

from django.conf import settings
from django.test import TestCase, override_settings
from faker.proxy import Faker

from bot.exceptions import DiscordApiException
from bot.utils import discord_api_get, discord_api_patch, discord_api_post
from tests.bot.helpers.constants import (CHANNEL, LITECORD_API_URL, LITECORD_TOKEN, USER_WITH_DIFFERENT_SERVER,
                                         USER_WITH_SAME_SERVER)
from tests.utils import check_litecord_connection


@unittest.skipIf(not check_litecord_connection(), 'Litecord seems to be unreachable')
@override_settings(DISCORD_API_URL=LITECORD_API_URL, BOT_TOKEN=LITECORD_TOKEN)
class TestDiscordApiRequest(TestCase):

    def setUp(self):
        self.faker = Faker()
        self.users_url = f'{settings.DISCORD_API_URL}users'
        self.bot_url = f'{self.users_url}/@me'
        self.dm_url = f'{self.users_url}/@me/channels'
        self.channels_url = f'{settings.DISCORD_API_URL}channels'

    def test_discord_api_get_ok(self):
        url = f'{self.users_url}/{USER_WITH_SAME_SERVER}'
        response = discord_api_get(url)

        self.assertEqual(200, response.status_code)

    def test_discord_api_get_ko(self):
        url = f'{self.dm_url}/{self.faker.pyint(min_value=1)}'

        with self.assertRaises(DiscordApiException) as ex:
            discord_api_get(url)
        ex = ex.exception
        self.assertEqual(404, ex.error_code)

    def test_discord_api_post_ok(self):
        data = {
            'recipient_id': USER_WITH_SAME_SERVER
        }
        response = discord_api_post(f'{self.dm_url}', data=data)

        self.assertEqual(200, response.status_code)

    # Accessing unexistent user as bot
    @override_settings(BOT_TOKEN='this_is_an_unexistent_token')
    def test_discord_api_post_ko(self):
        data = {
            'recipient_id': USER_WITH_DIFFERENT_SERVER
        }

        with self.assertRaises(DiscordApiException) as ex:
            discord_api_post(f'{self.dm_url}', data=data)
        ex = ex.exception
        self.assertEqual(401, ex.error_code)

    def test_discord_api_patch_ok(self):
        url = f'{self.channels_url}/{CHANNEL}'
        msg_url = f'{url}/messages'
        msg_json = discord_api_post(msg_url, data={'content': self.faker.word()}).json()
        msg_id = msg_json['id']
        url = f'{msg_url}/{msg_id}'
        response = discord_api_patch(url, data={'content': self.faker.word()})

        self.assertEqual(200, response.status_code)

    def test_discord_api_patch_ko(self):
        url = f'{self.channels_url}/{CHANNEL}/messages/{self.faker.pyint(min_value=1)}'

        with self.assertRaises(DiscordApiException) as ex:
            discord_api_patch(url, data={'content': self.faker.word()})
        ex = ex.exception
        self.assertEqual(ex.error_code, 403)

    def test_internal_server_error(self):
        url = f'{self.dm_url}'
        data = {
            'recipient_id': self.faker.pyint(min_value=1)
        }

        with self.assertRaises(DiscordApiException) as ex:
            discord_api_post(url, data=data)
        ex = ex.exception
        self.assertEqual(500, ex.error_code)
