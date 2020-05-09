from django.test import TestCase

from common.templatetags.string_utils import startswith


class TestStartsWithTemplateTag(TestCase):

    def setUp(self):
        self.text = 'thisIsText'

    def test_startswith_ok(self):
        self.assertTrue(startswith(self.text, 'thisIs'))

    def test_startswith_ko(self):
        self.assertFalse(startswith(self.text, 'thisIsNot'))
