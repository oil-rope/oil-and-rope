from django.apps import apps
from django.shortcuts import reverse
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APITestCase

from common.constants import models

User = apps.get_model(models.USER_MODEL)

base_resolver = 'api:dynamic_menu'


class TestChatAPIRootViewSet(APITestCase):

    def test_non_authenticated_list_urls_ok(self):
        url = reverse(f'{base_resolver}:api-root')
        response = self.client.get(url)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_authenticated_not_admin_list_urls_ko(self):
        user = baker.make(User)
        self.client.force_login(user)
        url = reverse(f'{base_resolver}:api-root')
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
