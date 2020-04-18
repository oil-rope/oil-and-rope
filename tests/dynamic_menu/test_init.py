from django.test import TestCase

from dynamic_menu import get_version


class TestGetVersion(TestCase):

    def setUp(self):
        self.clean_version = (1, 0, 0)
        self.beta_version = (1, 0, 0, 'BETA')
        self.string_version = ('1', '0', '0')
        self.ofuscated_version = (1, 0, 0, 'BETA', 0, 2)

    def test_get_version(self):
        expected = '1.0.0'
        result = get_version(self.clean_version)
        self.assertEqual(expected, result)

        expected = '1.0.0_BETA'
        result = get_version(self.beta_version)
        self.assertEqual(expected, result)

        expected = '1.0.0'
        result = get_version(self.string_version)
        self.assertEqual(expected, result)

        expected = '1.0.0_BETA.0.2'
        result = get_version(self.ofuscated_version)
        self.assertEqual(expected, result)
