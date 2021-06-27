from django.apps import apps
from django.shortcuts import reverse
from faker import Faker
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APITestCase

from common.constants import models

Domain = apps.get_model(models.DOMAIN_MODEL)
Place = apps.get_model(models.PLACE_MODEL)
User = apps.get_model(models.USER_MODEL)

fake = Faker()

base_resolver = 'api:roleplay'


class TestRoleplayAPIRoot(APITestCase):

    def test_anonymous_list_urls_ok(self):
        url = reverse(f'{base_resolver}:api-root')
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)


# noinspection DuplicatedCode
class TestDomainViewSet(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.list_url = reverse(f'{base_resolver}:domain-list')
        cls.model = Domain

        cls.user = baker.make(User)
        cls.admin_user = baker.make(User, is_staff=True)

    def test_anonymous_domain_list_ko(self):
        response = self.client.get(self.list_url)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_authenticated_not_admin_domain_list_ok(self):
        self.client.force_login(self.user)
        response = self.client.get(self.list_url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_authenticated_admin_domain_list_ok(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(self.list_url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_authenticated_not_admin_domain_detail_ok(self):
        self.client.force_login(self.user)
        domain = baker.make(self.model)
        url = reverse(f'{base_resolver}:domain-detail', kwargs={'pk': domain.pk})
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_authenticated_admin_domain_detail_ok(self):
        self.client.force_login(self.admin_user)
        domain = baker.make(self.model)
        url = reverse(f'{base_resolver}:domain-detail', kwargs={'pk': domain.pk})
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)


class TestPlaceViewSet(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.model = Place
        cls.list_url = reverse(f'{base_resolver}:place-list')

        cls.user = baker.make(User)
        cls.admin_user = baker.make(User, is_staff=True)

    def test_anonymous_place_list_ko(self):
        response = self.client.get(self.list_url)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_authenticated_not_admin_owner_list_ok(self):
        self.client.force_login(self.user)
        baker.make(_model=self.model, _quantity=fake.pyint(min_value=1, max_value=10), owner=self.user)
        baker.make(_model=self.model, _quantity=fake.pyint(min_value=1, max_value=10))
        response = self.client.get(self.list_url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_data = self.model.objects.filter(
            owner=self.user
        ).count()
        data = response.json()

        self.assertEqual(expected_data, len(data))
