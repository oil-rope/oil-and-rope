import random
from unittest import mock

from django.conf import settings
from django.core.exceptions import ValidationError
from django.test import TestCase

from common.validators import files


class TestFileValidators(TestCase):

    def setUp(self):
        self.file_mock = mock.MagicMock()
        self.file_mock.size = settings.FILE_UPLOAD_MAX_MEMORY_SIZE + random.randint(1, 10000)

    def test_validate_file_size(self):
        with self.assertRaises(ValidationError) as ex:
            files.validate_file_size(self.file_mock)
        exception = ex.exception
        self.assertRegex(exception.message, '.*File too large.*')

    def test_validate_music_file(self):
        files.validate_music_file(self.file_mock)
