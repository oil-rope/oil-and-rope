from django.shortcuts import reverse
from django.test import TestCase, override_settings
from model_bakery import baker

from chat import views
from common.constants import models


class TestChatView(TestCase):
    view = views.ChatView
    resolver = 'chat:index'

    @classmethod
    def setUpTestData(cls):
        cls.user = baker.make(models.USER_MODEL)
        cls.superuser = baker.make(models.USER_MODEL, is_superuser=True)
        cls.chat = baker.make(models.CHAT_MODEL)

    def setUp(self):
        self.url = reverse(self.resolver)

    def test_anonymous_user_access_ko(self):
        login_url = reverse('registration:login')
        response = self.client.get(self.url)
        expected_url = f'{login_url}?next={self.url}'

        self.assertRedirects(response, expected_url)

    def test_non_superuser_access_ko(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(403, response.status_code)

    def test_superuser_access_ok(self):
        self.client.force_login(self.superuser)
        response = self.client.get(self.url)

        self.assertEqual(200, response.status_code)

    @override_settings(WS_HOST='localhost:8000')
    def test_access_with_ws_host_ok(self):
        self.client.force_login(self.superuser)
        response = self.client.get(self.url)

        self.assertEqual(200, response.status_code)
