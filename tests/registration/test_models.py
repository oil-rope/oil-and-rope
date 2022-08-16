import unittest

from django.apps import apps
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.utils import timezone
from freezegun import freeze_time
from model_bakery import baker

from common.constants import models as constants

from .. import fake
from ..bot.helpers.constants import LITECORD_API_URL, LITECORD_TOKEN, USER_WITH_SAME_SERVER
from ..utils import check_litecord_connection

Place = apps.get_model(constants.ROLEPLAY_PLACE)
Race = apps.get_model(constants.ROLEPLAY_RACE)
Session = apps.get_model(constants.ROLEPLAY_SESSION)
User = apps.get_model(constants.REGISTRATION_USER)


class TestUser(TestCase):
    model = get_user_model()

    def setUp(self):
        self.instance = baker.make_recipe('registration.user')

    def test_owned_races_ok(self):
        iterations = fake.pyint(min_value=1, max_value=10)
        races = baker.make(Race, iterations)
        [r.add_owners(self.instance) for r in races]

        result = self.instance.owned_races.count()
        expected_result = iterations

        self.assertEqual(expected_result, result)

    def test_discord_user_none_when_discord_id_not_set_ok(self):
        self.assertIsNone(self.instance.discord_user)

    @unittest.skipIf(not check_litecord_connection(), 'Litecord seems to be unreachable.')
    @override_settings(DISCORD_API_URL=LITECORD_API_URL, BOT_TOKEN=LITECORD_TOKEN)
    def test_discord_user_with_discord_id_ok(self):
        self.instance.discord_id = USER_WITH_SAME_SERVER
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
