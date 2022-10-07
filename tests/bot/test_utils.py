from unittest.mock import MagicMock, patch

from django.test import TestCase
from requests import Request, Response

from bot.exceptions import DiscordApiException
from bot.utils import discord_api_get, discord_api_patch, discord_api_post
from tests.utils import fake


class TestDiscordApiRequest(TestCase):
    def setUp(self):
        response_mock = Response()
        response_mock.request = Request('GET')
        response_mock.status_code = 200

        self.response_mock = response_mock

        self.url = f'https://{fake.domain_name()}'

    @patch('requests.get')
    def test_discord_api_get_ok(self, mocker_requests_get: MagicMock):
        self.response_mock.request.method = 'GET'
        mocker_requests_get.return_value = self.response_mock

        response = discord_api_get(self.url)

        self.assertEqual(200, response.status_code)

    @patch('requests.get')
    def test_discord_api_get_ko(self, mocker_requests_get: MagicMock):
        self.response_mock.status_code = 404
        mocker_requests_get.return_value = self.response_mock

        with self.assertRaises(DiscordApiException) as ex:
            discord_api_get(self.url)
        self.assertEqual(404, ex.exception.error_code)

    @patch('requests.post')
    def test_discord_api_post_ok(self, mocker_requests_post: MagicMock):
        self.response_mock.request.method = 'POST'
        mocker_requests_post.return_value = self.response_mock
        data = fake.pydict(allowed_types=[str, int, float])

        response = discord_api_post(f'{self.url}', data=data)

        self.assertEqual(200, response.status_code)

    @patch('requests.post')
    def test_discord_api_post_ko(self, mocker_requests_post: MagicMock):
        self.response_mock.request.method = 'POST'
        self.response_mock.status_code = 401
        mocker_requests_post.return_value = self.response_mock
        data = fake.pydict(allowed_types=[str, int, float])

        with self.assertRaises(DiscordApiException) as ex:
            discord_api_post(self.url, data=data)

        self.assertEqual(401, ex.exception.error_code)

    @patch('requests.patch')
    def test_discord_api_patch_ok(self, mocker_requests_patch: MagicMock):
        self.response_mock.request.method = 'PATCH'
        mocker_requests_patch.return_value = self.response_mock
        data = fake.pydict(allowed_types=[str, int, float])

        response = discord_api_patch(self.url, data=data)

        self.assertEqual(200, response.status_code)

    @patch('requests.patch')
    def test_discord_api_patch_ko(self, mocker_requests_patch: MagicMock):
        self.response_mock.request.method = 'PATCH'
        self.response_mock.status_code = 403
        mocker_requests_patch.return_value = self.response_mock
        data = fake.pydict(allowed_types=[str, int, float])

        with self.assertRaises(DiscordApiException) as ex:
            discord_api_patch(self.url, data=data)

        self.assertEqual(ex.exception.error_code, 403)
