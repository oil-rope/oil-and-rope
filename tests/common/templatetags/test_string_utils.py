from django.shortcuts import reverse
from django.test import TestCase

from common.templatetags.string_utils import generate_breadcrumbs, startswith


class TestStartsWithTemplateFilter(TestCase):

    def setUp(self):
        self.text = 'thisIsText'

    def test_startswith_ok(self):
        self.assertTrue(startswith(self.text, 'thisIs'))

    def test_startswith_ko(self):
        self.assertFalse(startswith(self.text, 'thisIsNot'))


class TestGenerateBreadcrumbsFilter(TestCase):

    def setUp(self):
        self.text = 'Home=core:home,Worlds=roleplay:world_list'

    def test_generate_breadcrumbs_ok(self):
        expected = {
            'Home': reverse('core:home'),
            'Worlds': reverse('roleplay:world_list')
        }
        result = generate_breadcrumbs(self.text)

        self.assertDictEqual(expected, result)

    def test_invented_url_ok(self):
        text = 'Home=core:home,Worlds=invented_url'
        expected = {
            'Home': reverse('core:home'),
            'Worlds': '#no-url'
        }
        result = generate_breadcrumbs(text)

        self.assertDictEqual(expected, result)

    def test_no_url_given_ok(self):
        text = 'Home=core:home,Worlds'
        expected = {
            'Home': reverse('core:home'),
            'Worlds': '#no-url'
        }
        result = generate_breadcrumbs(text)

        self.assertDictEqual(expected, result)
