from django.apps import apps
from django.shortcuts import reverse
from django.test import TestCase
from faker import Faker
from model_bakery import baker
from rest_framework import status

from common.constants import models

fake = Faker()

User = apps.get_model(models.USER_MODEL)


class TestRegistrationViewSet(TestCase):
    base_resolver = 'api:registration'

    def test_non_authenticated_list_urls_ok(self):
        url = reverse(f'{self.base_resolver}:api-root')
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)


class TestUserViewSet(TestRegistrationViewSet):
    model = User

    @classmethod
    def setUpTestData(cls):
        cls.user = baker.make(cls.model)

    def test_non_authenticated_list_ko(self):
        url = reverse(f'{self.base_resolver}:user-list')
        response = self.client.get(url)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_authenticated_not_admin_user_list_ko(self):
        url = reverse(f'{self.base_resolver}:user-list')
        user = baker.make(self.model)
        self.client.force_login(user)
        response = self.client.get(url)

        self.assertTrue(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_authenticated_admin_user_list_ok(self):
        url = reverse(f'{self.base_resolver}:user-list')
        user = baker.make(self.model, is_staff=True)
        self.client.force_login(user)
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_authenticated_not_same_user_detail_ko(self):
        user_to_check = baker.make(self.model)
        url = reverse(f'{self.base_resolver}:user-detail', kwargs={'pk': user_to_check.pk})
        user = baker.make(self.model)
        self.client.force_login(user)
        response = self.client.get(url)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_authenticated_same_user_detail_ok(self):
        user_to_check = baker.make(self.model)
        url = reverse(f'{self.base_resolver}:user-detail', kwargs={'pk': user_to_check.pk})
        self.client.force_login(user_to_check)
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_authenticated_admin_user_detail_ok(self):
        user_to_check = baker.make(self.model)
        url = reverse(f'{self.base_resolver}:user-detail', kwargs={'pk': user_to_check.pk})
        user = baker.make(self.model, is_staff=True)
        self.client.force_login(user)
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
