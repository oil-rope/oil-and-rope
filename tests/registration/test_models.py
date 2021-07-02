from django.apps import apps
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.utils import timezone
from faker import Faker
from freezegun import freeze_time
from model_bakery import baker

from common.constants import models as constants
from roleplay.enums import SiteTypes
from tests.bot.helpers.constants import LITECORD_API_URL, LITECORD_TOKEN, USER_WITH_SAME_SERVER

Place = apps.get_model(constants.PLACE_MODEL)
Race = apps.get_model(constants.RACE_MODEL)
Session = apps.get_model(constants.SESSION_MODEL)
User = apps.get_model(constants.USER_MODEL)

fake = Faker()


class TestUser(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.model = get_user_model()

        cls.instance = baker.make(_model=cls.model)
        cls.discord_user = baker.make(
            _model=constants.DISCORD_USER_MODEL,
            id=USER_WITH_SAME_SERVER,
            user=cls.instance,
        )

    def test_get_user_from_discord_api_ko(self):
        user = baker.make(_model=self.model)
        discord_user = user.get_user_from_discord_api()

        self.assertIsNone(discord_user)

    @override_settings(DISCORD_API_URL=LITECORD_API_URL, BOT_TOKEN=LITECORD_TOKEN)
    def test_get_user_from_discord_api_ok(self):
        discord_user = self.instance.get_user_from_discord_api()
        self.assertIsNotNone(discord_user)

    def test_owned_races_ok(self):
        iterations = fake.pyint(min_value=1, max_value=10)
        races = baker.make(Race, iterations)
        [r.add_owners(self.instance) for r in races]

        result = self.instance.owned_races.count()
        expected_result = iterations

        self.assertEqual(expected_result, result)

    def test_gm_sessions_ok(self):
        iterations = fake.pyint(min_value=1, max_value=10)
        world = baker.make(Place, site_type=SiteTypes.WORLD)
        sessions = baker.make(_model=Session, _quantity=iterations, world=world)
        [s.add_game_masters(self.instance) for s in sessions]

        result = self.instance.gm_sessions.count()
        expected_result = iterations

        self.assertEqual(expected_result, result)


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
