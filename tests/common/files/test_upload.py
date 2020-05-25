from django.contrib.auth import get_user_model
from django.test import TestCase
from faker import Faker
from freezegun import freeze_time
from model_bakery import baker

from common.files.upload import default_upload_to


class TestUpload(TestCase):

    def setUp(self):
        self.faker = Faker()
        self.filename = self.faker.file_name(category='image')
        self.instance = baker.make(get_user_model())

    @freeze_time('2020-01-01')
    def test_default_upload_to_with_identifier(self):
        expected = 'auth/user/2020/01/01/1/' + self.filename
        result = default_upload_to(self.instance, self.filename)
        self.assertEqual(expected, result)
