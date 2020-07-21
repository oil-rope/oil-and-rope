import random
from unittest import mock

from django.conf import settings
from django.core.exceptions import ValidationError
from django.test import TestCase
from faker import Faker

from common.validators import files


class TestFileValidators(TestCase):

    def setUp(self):
        self.faker = Faker()
        self.file_mock = mock.MagicMock()

    def test_validate_file_size(self):
        self.file_mock.size = settings.FILE_UPLOAD_MAX_MEMORY_SIZE + random.randint(1, 10000)
        with self.assertRaisesRegex(ValidationError, r'.*File too large.*'):
            files.validate_file_size(self.file_mock)

    def test_validate_music_file(self):
        self.file_mock.name = self.faker.file_name('image')
        with self.assertRaisesRegex(ValidationError, r'.*File is not an audio.*'):
            files.validate_music_file(self.file_mock)
