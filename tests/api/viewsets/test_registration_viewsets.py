from django.apps import apps
from django.shortcuts import reverse
from django.test import TestCase
from model_bakery import baker
from rest_framework import status

from common.constants import models

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

    def test_authenticated_not_admin_user_ko(self):
        url = reverse(f'{self.base_resolver}:user-list')
        user = baker.make(self.model)
        self.client.force_login(user)
        response = self.client.get(url)

        self.assertTrue(status.HTTP_403_FORBIDDEN, response.status_code)
