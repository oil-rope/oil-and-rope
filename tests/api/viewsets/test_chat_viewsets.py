from django.apps import apps
from django.shortcuts import reverse
from django.test import TestCase
from model_bakery import baker
from rest_framework import status

from common.constants import models

Chat = apps.get_model(models.CHAT_MODEL)
User = apps.get_model(models.USER_MODEL)

base_resolver = 'api:chat'


class TestChatAPIRootViewSet(TestCase):

    def test_non_authenticated_list_urls_ok(self):
        url = reverse(f'{base_resolver}:api-root')
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)


class TestChatViewSet(TestCase):
    model = Chat

    @classmethod
    def setUpTestData(cls):
        cls.user = baker.make(User)
        cls.admin_user = baker.make(User, is_staff=True)

    def test_non_authenticated_list_ko(self):
        url = reverse(f'{base_resolver}:chat-list')
        response = self.client.get(url)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_authenticated_chat_list_ok(self):
        url = reverse(f'{base_resolver}:chat-list')
        self.client.force_login(self.user)
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_authenticated_admin_chat_list_ok(self):
        url = reverse(f'{base_resolver}:chat-list')
        self.client.force_login(self.admin_user)
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
