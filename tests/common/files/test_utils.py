from django.test import TestCase

from common.files import utils


class TestFileUtils(TestCase):

    def test_max_size_file_mb(self):
        expected = 6
        result = utils.max_size_file_mb()

        self.assertEqual(expected, result)

    def test_max_size_file_mb_floating(self):
        with self.settings(FILE_UPLOAD_MAX_MEMORY_SIZE=2621440):
            expected = 2.5
            result = utils.max_size_file_mb()

            self.assertEqual(expected, result)
