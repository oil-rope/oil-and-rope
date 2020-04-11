from django.contrib.auth import get_user_model
from django.http.cookie import SimpleCookie
from django.test import TestCase
from model_bakery import baker

from faker import Faker
from dynamic_menu.models import DynamicMenu


class TestMenuContextProcessor(TestCase):

    def setUp(self):
        self.faker = Faker()
        self.user = baker.make(get_user_model())
        self.url = '/'

    def test_context_processor_exists_ok(self):
        response = self.client.get(self.url, follow=True)
        self.assertIn('menus', response.context, 'Variable \'menus\' not found in context.')
        self.assertIn('context_menus', response.context, 'Variable \'context_menus\' not found in context.')

        self.client.force_login(self.user)
        response = self.client.get(self.url, follow=True)
        self.assertIn('menus', response.context, 'Variable \'menus\' not found in context.')
        self.assertIn('context_menus', response.context, 'Variable \'context_menus\' not found in context.')

    def test_context_processor_content_ok(self):
        main_menus = baker.make(DynamicMenu, 3, menu_type=DynamicMenu.MAIN_MENU)
        response = self.client.get(self.url, follow=True)
        expected = response.context['menus']
        for main_menu in main_menus:
            self.assertIn(main_menu, expected)

        parent = main_menus[0]
        context_menus = baker.make(DynamicMenu, 3, menu_type=DynamicMenu.CONTEXT_MENU, parent=parent)
        self.client.cookies = SimpleCookie({'_auth_user_menu_referrer': parent.id})
        response = self.client.get(self.url, follow=True)
        expected = response.context['context_menus']
        for context_menu in context_menus:
            self.assertIn(context_menu, expected)

    def test_access_wrong_menu_referrer_ko(self):
        main_menu = baker.make(DynamicMenu, menu_type=DynamicMenu.MAIN_MENU)
        baker.make(DynamicMenu, menu_type=DynamicMenu.CONTEXT_MENU, parent=main_menu)
        self.client.cookies = SimpleCookie({'_auth_user_menu_referrer': self.faker.random_int(2, 20)})
        request = self.client.get(self.url, follow=True).wsgi_request
        self.assertIsNone(request.COOKIES['_auth_user_menu_referrer'])
