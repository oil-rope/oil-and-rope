from django.apps import apps
from django.shortcuts import reverse
from faker import Faker
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APITestCase

from common.constants import models

DynamicMenu = apps.get_model(models.DYNAMIC_MENU)
User = apps.get_model(models.USER_MODEL)

fake = Faker()

base_resolver = 'api:dynamic_menu'


class TestDynamicMenuAPIRootViewSet(APITestCase):

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


class TestDynamicMenuViewSet(APITestCase):
    model = DynamicMenu

    @classmethod
    def setUpTestData(cls):
        cls.user = baker.make(User)
        cls.admin_user = baker.make(User, is_staff=True)
        cls.instance = baker.make(cls.model)

    def test_anonymous_dynamic_menu_list_ko(self):
        url = reverse(f'{base_resolver}:menu-list')
        response = self.client.get(url)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_authenticated_not_admin_dynamic_menu_list_ko(self):
        self.client.force_login(self.user)
        url = reverse(f'{base_resolver}:menu-list')
        response = self.client.get(url)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_authenticated_admin_dynamic_menu_list_ko(self):
        self.client.force_login(self.admin_user)
        url = reverse(f'{base_resolver}:menu-list')
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_anonymous_dynamic_menu_detail_ko(self):
        url = reverse(f'{base_resolver}:menu-detail', kwargs={'pk': self.instance.pk})
        response = self.client.get(url)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_authenticated_not_admin_dynamic_menu_detail_ko(self):
        self.client.force_login(self.user)
        url = reverse(f'{base_resolver}:menu-detail', kwargs={'pk': self.instance.pk})
        response = self.client.get(url)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_authenticated_admin_dynamic_menu_detail_ko(self):
        self.client.force_login(self.admin_user)
        url = reverse(f'{base_resolver}:menu-detail', kwargs={'pk': self.instance.pk})
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_anonymous_dynamic_menu_create_ko(self):
        url = reverse(f'{base_resolver}:menu-list')
        data = {
            'name': fake.word()
        }
        response = self.client.post(url, data=data)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_authenticated_not_admin_dynamic_menu_create_ko(self):
        self.client.force_login(self.user)
        url = reverse(f'{base_resolver}:menu-list')
        data = {
            'name': fake.word()
        }
        response = self.client.post(url, data=data)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_authenticated_admin_dynamic_menu_create_ko(self):
        self.client.force_login(self.admin_user)
        url = reverse(f'{base_resolver}:menu-list')
        data = {
            'name': fake.word()
        }
        response = self.client.post(url, data=data)

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

    def test_anonymous_dynamic_menu_update_ko(self):
        url = reverse(f'{base_resolver}:menu-detail', kwargs={'pk': self.instance.pk})
        data = {
            'name': fake.word()
        }
        response = self.client.put(url, data=data)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_authenticated_not_admin_dynamic_menu_update_ko(self):
        self.client.force_login(self.user)
        url = reverse(f'{base_resolver}:menu-detail', kwargs={'pk': self.instance.pk})
        data = {
            'name': fake.word()
        }
        response = self.client.put(url, data=data)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_authenticated_admin_dynamic_menu_update_ko(self):
        self.client.force_login(self.admin_user)
        url = reverse(f'{base_resolver}:menu-detail', kwargs={'pk': self.instance.pk})
        data = {
            'name': fake.word()
        }
        response = self.client.put(url, data=data)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
