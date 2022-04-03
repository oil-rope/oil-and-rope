from django.shortcuts import resolve_url
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APITestCase

from oilandrope import __version__


class TestApiVersionView(APITestCase):
    resolver = 'api:version'

    @classmethod
    def setUpTestData(cls):
        cls.url = resolve_url(cls.resolver)

    def test_get_method_ok(self):
        response = self.client.get(self.url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_post_method_ko(self):
        response = self.client.post(self.url)

        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)

    def test_put_method_ko(self):
        response = self.client.put(self.url)

        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)

    def test_delete_method_ko(self):
        response = self.client.delete(self.url)

        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)

    def test_expected_version_ok(self):
        response = self.client.get(self.url)

        self.assertEqual(__version__, response.json()['version'])


class TestURLResolverViewSet(APITestCase):
    resolver = 'api:utils:resolver'

    @classmethod
    def setUpTestData(cls):
        cls.user = baker.make_recipe('registration.user')
        cls.url = resolve_url(cls.resolver)

    def test_access_get_method_not_allowed_ko(self):
        response = self.client.get(self.url)

        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)

    def test_resolver_without_params_ok(self):
        data = {
            'resolver': 'core:home',
        }
        response = self.client.post(self.url, data)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_expected_url_without_params_ok(self):
        data = {
            'resolver': 'core:home',
        }
        response = self.client.post(self.url, data)
        expected_url = resolve_url('core:home')
        url = response.json()['url']

        self.assertEqual(expected_url, url)

    def test_non_existent_url_ok(self):
        data = {
            'resolver': 'random',
        }
        response = self.client.post(self.url, data)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_url = '#no-url'
        url = response.json()['url']

        self.assertEqual(expected_url, url)

    def test_without_resolver_ko(self):
        data = {
            'pk': 1
        }
        response = self.client.post(self.url, data)

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_with_params_ok(self):
        place = baker.make_recipe('roleplay.place')
        data = {
            'resolver': 'roleplay:place:detail',
            'pk': place.pk,
        }
        response = self.client.post(self.url, data)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_url = resolve_url(place)
        url = response.json()['url']

        self.assertEqual(expected_url, url)


class TestRollView(APITestCase):
    resolver = 'api:utils:roll_dice'

    @classmethod
    def setUpTestData(cls):
        cls.user = baker.make_recipe('registration.user')
        cls.url = resolve_url(cls.resolver)

    def test_anonymous_access_ko(self):
        response = self.client.get(self.url)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_user_logged_get_method_ko(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)

    def test_user_logged_put_method_ko(self):
        self.client.force_login(self.user)
        response = self.client.put(self.url)

        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)

    def test_user_logged_delete_method_ko(self):
        self.client.force_login(self.user)
        response = self.client.delete(self.url)

        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)

    def test_user_logged_post_method_ok(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url)

        self.assertNotEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)

    def test_user_logged_post_method_without_data_ko(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url)

        self.assertListEqual(['\'roll\' field is required.'], response.json())

    def test_user_logged_post_method_with_invalid_data_ko(self):
        self.client.force_login(self.user)
        data = {
            'roll': '1d20+',
        }
        response = self.client.post(self.url, data=data)

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertListEqual(['Dice roll `1d20+` syntax is incorrect.'], response.json())

    def test_user_logged_post_method_with_valid_data_ko(self):
        self.client.force_login(self.user)
        data = {
            'roll': '4d6+2+2-1+2d6',
        }
        response = self.client.post(self.url, data=data)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
