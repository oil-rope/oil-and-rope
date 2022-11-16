from unittest.mock import MagicMock, patch

from django.apps import apps
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from freezegun import freeze_time
from model_bakery import baker

from common.constants import models as constants
from tests.mocks import discord
from tests.utils import fake

Place = apps.get_model(constants.ROLEPLAY_PLACE)
Race = apps.get_model(constants.ROLEPLAY_RACE)
Session = apps.get_model(constants.ROLEPLAY_SESSION)
User = apps.get_model(constants.REGISTRATION_USER)


class TestUser(TestCase):
    model = get_user_model()

    def setUp(self):
        self.instance = baker.make_recipe('registration.user')

    def test_discord_user_none_when_discord_id_not_set_ok(self):
        self.assertIsNone(self.instance.discord_user)

    @patch('bot.utils.discord_api_request')
    def test_discord_user_with_discord_id_ok(self, mocker_api_request: MagicMock):
        discord_id = f'{fake.random_number(digits=18)}'
        mocker_api_request.return_value = discord.user_response(id=discord_id)

        self.instance.discord_id = discord_id
        self.instance.save(update_fields=['discord_id'])
        self.instance.refresh_from_db()

        self.assertIsNotNone(self.instance.discord_user)


class TestProfileModel(TestCase):

    def setUp(self):
        self.user = baker.make(get_user_model())
        self.profile = self.user.profile
        self.profile.birthday = timezone.datetime(1998, 7, 14).date()
        self.profile.save()

    @freeze_time("2020-01-01")
    def test_get_age_ok(self):
        expected = 21
        result = self.profile.age
        self.assertEqual(expected, result)

    def test_str_ok(self):
        expected = 'Profile {}'.format(self.user.username)
        self.assertEqual(expected, str(self.profile))
