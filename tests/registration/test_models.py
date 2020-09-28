from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from faker import Faker
from freezegun import freeze_time
from model_bakery import baker


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
