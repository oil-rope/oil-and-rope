from django.apps import apps
from django.shortcuts import reverse
from faker import Faker
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APITestCase

from common.constants import models

fake = Faker()

User = apps.get_model(models.USER_MODEL)
Profile = apps.get_model(models.PROFILE_MODEL)

base_resolver = 'api:registration'


class TestRegistrationViewSet(APITestCase):

    def test_non_authenticated_list_urls_ok(self):
        url = reverse(f'{base_resolver}:api-root')
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)


class TestUserViewSet(APITestCase):
    model = User

    def test_non_authenticated_list_ko(self):
        url = reverse(f'{base_resolver}:user-list')
        response = self.client.get(url)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_authenticated_not_admin_user_list_ko(self):
        url = reverse(f'{base_resolver}:user-list')
        user = baker.make(self.model)
        self.client.force_login(user)
        response = self.client.get(url)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_authenticated_admin_user_list_ok(self):
        url = reverse(f'{base_resolver}:user-list')
        user = baker.make(self.model, is_staff=True)
        self.client.force_login(user)
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_authenticated_get_current_user_ok(self):
        url = reverse(f'{base_resolver}:user-detail', kwargs={'pk': '@me'})
        user = baker.make(self.model)
        self.client.force_login(user)
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_authenticated_not_same_user_detail_ko(self):
        user_to_check = baker.make(self.model)
        url = reverse(f'{base_resolver}:user-detail', kwargs={'pk': user_to_check.pk})
        user = baker.make(self.model)
        self.client.force_login(user)
        response = self.client.get(url)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_authenticated_same_user_detail_ok(self):
        user_to_check = baker.make(self.model)
        url = reverse(f'{base_resolver}:user-detail', kwargs={'pk': user_to_check.pk})
        self.client.force_login(user_to_check)
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_authenticated_admin_user_detail_ok(self):
        user_to_check = baker.make(self.model)
        url = reverse(f'{base_resolver}:user-detail', kwargs={'pk': user_to_check.pk})
        user = baker.make(self.model, is_staff=True)
        self.client.force_login(user)
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)


class TestProfileViewSet(TestRegistrationViewSet):
    model = Profile

    def test_non_authenticated_list_ko(self):
        url = reverse(f'{base_resolver}:profile-list')
        response = self.client.get(url)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_authenticated_not_admin_user_list_ko(self):
        url = reverse(f'{base_resolver}:profile-list')
        user = baker.make(User)
        self.client.force_login(user)
        response = self.client.get(url)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_authenticated_admin_user_list_ok(self):
        url = reverse(f'{base_resolver}:profile-list')
        user = baker.make(User, is_staff=True)
        self.client.force_login(user)
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_authenticated_get_current_profile_ok(self):
        url = reverse(f'{base_resolver}:profile-detail', kwargs={'pk': '@me'})
        user = baker.make(User)
        self.client.force_login(user)
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_authenticated_not_same_user_detail_ko(self):
        profile_to_check = baker.make(User).profile
        url = reverse(f'{base_resolver}:profile-detail', kwargs={'pk': profile_to_check.pk})
        user = baker.make(User)
        self.client.force_login(user)
        response = self.client.get(url)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_authenticated_same_user_detail_ok(self):
        user = baker.make(User)
        profile_to_check = user.profile
        url = reverse(f'{base_resolver}:profile-detail', kwargs={'pk': profile_to_check.pk})
        self.client.force_login(user)
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_authenticated_admin_user_detail_ok(self):
        profile_to_check = baker.make(User).profile
        url = reverse(f'{base_resolver}:profile-detail', kwargs={'pk': profile_to_check.pk})
        user = baker.make(User, is_staff=True)
        self.client.force_login(user)
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
