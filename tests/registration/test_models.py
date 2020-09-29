from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.utils import timezone
from faker import Faker
from freezegun import freeze_time
from model_bakery import baker

from common.constants import models
from tests.bot.helpers.constants import LITECORD_API_URL, LITECORD_TOKEN, USER_WITH_SAME_SERVER


class TestUser(TestCase):
    fake = Faker()
    model = get_user_model()

    @classmethod
    def setUpTestData(cls):
        cls.instance = baker.make(_model=cls.model)
        cls.discord_user = baker.make(
            _model=models.DISCORD_USER_MODEL,
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


class TestProfileModel(TestCase):

    def setUp(self):
        self.faker = Faker()
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
