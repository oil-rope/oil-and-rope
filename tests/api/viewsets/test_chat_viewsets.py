from django.apps import apps
from django.shortcuts import reverse
from django.test import TestCase
from faker import Faker
from model_bakery import baker
from rest_framework import status

from common.constants import models

fake = Faker()

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

    def test_authenticated_chat_list_only_user_ok(self):
        """
        Checks if user can only see its own chat.
        """

        url = reverse(f'{base_resolver}:chat-list')
        self.client.force_login(self.user)

        # Creating data
        baker.make(_model=self.model, _quantity=fake.pyint(min_value=1, max_value=10))
        baker.make(_model=self.model, _quantity=fake.pyint(min_value=1, max_value=10), users=[self.user])
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        data = response.json()
        expected_data = self.model.objects.filter(
            users__in=[self.user],
        ).count()

        self.assertEqual(expected_data, len(data))

    def test_authenticated_admin_chat_list_ok(self):
        """
        Checks if admin can list every chat.
        """

        url = reverse(f'{base_resolver}:chat-list')
        self.client.force_login(self.admin_user)

        # Creating data
        baker.make(_model=self.model, _quantity=fake.pyint(min_value=1, max_value=10))
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        data = response.json()
        expected_data = self.model.objects.count()

        self.assertEqual(expected_data, len(data))

    def test_non_authenticated_detail_ko(self):
        chat = baker.make(self.model)
        url = reverse(f'{base_resolver}:chat-detail', kwargs={'pk': chat.pk})
        response = self.client.get(url)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_authenticated_user_not_in_chat_detail_ko(self):
        chat = baker.make(self.model)
        url = reverse(f'{base_resolver}:chat-detail', kwargs={'pk': chat.pk})
        self.client.force_login(self.user)
        response = self.client.get(url)

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_authenticated_user_in_chat_detail_ok(self):
        chat = baker.make(self.model, users=[self.user])
        baker.make(_model=self.model, _quantity=fake.pyint(min_value=1, max_value=10))

        url = reverse(f'{base_resolver}:chat-detail', kwargs={'pk': chat.pk})
        self.client.force_login(self.user)
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
