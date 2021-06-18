from django.shortcuts import reverse
from django.test import TestCase
from model_bakery import baker
from rest_framework import status

from common.constants import models


class TestRegistration(TestCase):
    base_resolver = 'api:registration'

    def test_user_list_ok(self):
        url = reverse(f'{self.base_resolver}:user-list')
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_user_detail_ko(self):
        user = baker.make(models.USER_MODEL)
        url = reverse(f'{self.base_resolver}:user-detail', kwargs={'pk': user.pk})
        response = self.client.get(url)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_user_detail_ok(self):
        user = baker.make(models.USER_MODEL)
        self.client.force_login(user)
        url = reverse(f'{self.base_resolver}:user-detail', kwargs={'pk': user.pk})
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_profile_list_ok(self):
        url = reverse(f'{self.base_resolver}:profile-list')
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_profile_detail_ko(self):
        user = baker.make(models.USER_MODEL)
        url = reverse(f'{self.base_resolver}:profile-detail', kwargs={'pk': user.profile.pk})
        response = self.client.get(url)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_profile_detail_ok(self):
        user = baker.make(models.USER_MODEL)
        self.client.force_login(user)
        url = reverse(f'{self.base_resolver}:profile-detail', kwargs={'pk': user.profile.pk})
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
