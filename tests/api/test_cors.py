from django.apps import apps
from django.shortcuts import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from common.constants import models
from common.utils import create_faker

fake = create_faker()

User = apps.get_model(models.USER_MODEL)


class TestAPICors(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.username = fake.user_name()
        cls.password = fake.password()
        cls.user = User.objects.create_user(username=cls.username, password=cls.password)
        cls.token = Token.objects.create(user=cls.user)
        cls.headers = {
            'HTTP_ACCEPT': 'application/json',
            'HTTP_CONTENT_TYPE': 'application/json',
            'HTTP_ORIGIN': fake.domain_name(),
            'HTTP_HOST': 'testserver',
            'HTTP_PRAGMA': 'no-cache',
            'HTTP_CACHE_CONTROL': 'no-cache',
            'HTTP_USER_AGENT': fake.user_agent(),
        }
        cls.auth_headers = cls.headers.copy()
        cls.auth_headers.update({
            'HTTP_AUTHORIZATION': f'Token {cls.token.key}'
        })

    def setUp(self):
        self.client.credentials(**self.headers)

    def test_get_api_ok(self):
        url = reverse('api:version')
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_get_token_ok(self):
        url = reverse('api:token')
        data = {
            'username': self.user.username,
            'password': self.password,
        }
        response = self.client.post(url, data)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_data = self.token.key
        data = response.json()['token']

        self.assertEqual(expected_data, data)

    def test_get_authenticated_user_ok(self):
        url = reverse('api:registration:user-detail', kwargs={'pk': '@me'})
        self.client.credentials(**self.auth_headers)
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
