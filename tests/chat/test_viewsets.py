from django.shortcuts import reverse
from django.test import TestCase
from model_bakery import baker
from rest_framework.test import APIClient

from common.constants import models


class TestChatViewSet(TestCase):
    resolver_list = 'chat:api:chat-list'
    resolver_detail = 'chat:api:chat-detail'

    @classmethod
    def setUpTestData(cls):
        cls.user = baker.make(models.USER_MODEL, is_staff=False)
        cls.staff_user = baker.make(models.USER_MODEL, is_staff=True)

        cls.chat = baker.make(models.CHAT_MODEL)
        cls.user_with_chat = baker.make(models.USER_MODEL, is_staff=False)
        cls.chat.users.add(cls.user_with_chat)

    def setUp(self):
        self.client = APIClient()
        self.list_url = reverse(self.resolver_list)
        self.detail_url = reverse(self.resolver_detail, kwargs={'pk': self.chat.pk})

    def test_access_list_anonymous_user_ko(self):
        response = self.client.get(self.list_url)

        self.assertEqual(403, response.status_code)

    def test_access_list_user_not_in_chat_ko(self):
        self.client.force_login(self.user)
        response = self.client.get(self.list_url)

        self.assertEqual(403, response.status_code)

    def test_access_list_user_in_chat_ko(self):
        self.client.force_login(self.user_with_chat)
        response = self.client.get(self.list_url)

        self.assertEqual(403, response.status_code)

    def test_access_list_staff_user_ok(self):
        self.client.force_login(self.staff_user)
        response = self.client.get(self.list_url)

        self.assertEqual(200, response.status_code)

    def test_access_detail_anonymous_user_ko(self):
        response = self.client.get(self.detail_url)

        self.assertEqual(403, response.status_code)

    def test_access_detail_user_not_in_chat_ko(self):
        self.client.force_login(self.user)
        response = self.client.get(self.detail_url)

        self.assertEqual(403, response.status_code)

    def test_access_detail_user_in_chat_ok(self):
        self.client.force_login(self.user_with_chat)
        response = self.client.get(self.detail_url)

        self.assertEqual(200, response.status_code)

    def test_access_detail_staff_user_ok(self):
        self.client.force_login(self.staff_user)
        response = self.client.get(self.detail_url)

        self.assertEqual(200, response.status_code)
