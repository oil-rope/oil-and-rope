from django.shortcuts import reverse
from django.test import TestCase
from model_bakery import baker

from common.templatetags.string_utils import (capfirstletter, generate_breadcrumbs, startswith, verbose_name,
                                              verbose_name_plural)
from registration.models import User


class TestStartsWithTemplateFilter(TestCase):

    def setUp(self):
        self.text = 'thisIsText'

    def test_startswith_ok(self):
        self.assertTrue(startswith(self.text, 'thisIs'))

    def test_startswith_ko(self):
        self.assertFalse(startswith(self.text, 'thisIsNot'))


class TestGenerateBreadcrumbsFilter(TestCase):

    def setUp(self):
        self.text = 'Home=core:home,Worlds=roleplay:world:list'

    def test_generate_breadcrumbs_ok(self):
        expected = {
            'Home': reverse('core:home'),
            'Worlds': reverse('roleplay:world:list')
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


class TestCapFirstLetterFilter(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.text = '¿¡¿pregunta?!?'

    def test_capfirstletter_ok(self):
        self.assertEqual('¿¡¿Pregunta?!?', capfirstletter(self.text))


class TestVerboseName(TestCase):
    def test_verbose_name_for_object_ok(self):
        user: User = baker.make_recipe('roleplay.user')

        self.assertEqual('user', verbose_name(user))

    def test_verbose_name_for_field_ok(self):
        user: User = baker.make_recipe('roleplay.user')

        self.assertEqual('discord identifier', verbose_name(user, 'discord_id'))

    def test_verbose_name_plural_for_object_ok(self):
        user: User = baker.make_recipe('roleplay.user')

        self.assertEqual('users', verbose_name_plural(user))
