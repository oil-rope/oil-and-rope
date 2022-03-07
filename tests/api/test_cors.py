import requests
from django.apps import apps
from django.conf import settings
from django.shortcuts import resolve_url
from django.test import LiveServerTestCase
from model_bakery import baker
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
        url = resolve_url('api:version')
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_get_token_ok(self):
        url = resolve_url('api:token')
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
        url = resolve_url('api:registration:user-detail', pk='@me')
        self.client.credentials(**self.auth_headers)
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)


class TestLiveAPICORS(LiveServerTestCase):

    def setUp(self):
        self.user = baker.make_recipe('registration.user')
        self.password = fake.password()
        self.user.set_password(self.password)
        self.user.save(update_fields=['password'])
        self.headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Origin': fake.domain_name(),
            'Host': 'testserver',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'User-Agent': fake.user_agent(),
        }

    def get_cookie_session(self):
        self.client.force_login(self.user)
        session_cookie = self.client.cookies[settings.SESSION_COOKIE_NAME]

        return {
            settings.SESSION_COOKIE_NAME: session_cookie.value
        }

    def test_authenticated_user_just_with_cookie_ok(self):
        user_url = resolve_url('api:registration:user-detail', pk='@me')
        url = f'{self.live_server_url}{user_url}'
        session_cookie = self.get_cookie_session()

        response = requests.get(url=url, headers=self.headers, cookies=session_cookie)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(response.json()['username'], self.user.username)
