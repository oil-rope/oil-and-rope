from django.test import TestCase
from faker import Faker
from django.contrib.auth import get_user_model
from model_bakery import baker

from django.utils.timezone import datetime
from registration.models import user_directory_path

from freezegun import freeze_time


class TestProfileModel(TestCase):

    def setUp(self):
        self.faker = Faker()
        self.user = baker.make(get_user_model())
        self.profile = self.user.profile
        self.profile.birthday = datetime(1998, 7, 14).date()
        self.profile.save()

    def test_user_directory_path_ok(self):
        file_name = self.faker.file_name(category='image')
        expected = 'user_{}/{}'.format(self.profile.user.pk, file_name)
        result = user_directory_path(self.profile, file_name)
        self.assertEqual(expected, result)

    @freeze_time("2020-01-01")
    def test_get_age_ok(self):
        expected = 21
        result = self.profile.age
        self.assertEqual(expected, result)

    def test_str_ok(self):
        expected = 'Profile {}'.format(self.user.username)
        self.assertEqual(expected, str(self.profile))
