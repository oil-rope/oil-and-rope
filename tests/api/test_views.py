from django.shortcuts import reverse
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APITestCase


class TestURLResolverViewSet(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = baker.make_recipe('registration.user')
        cls.url = reverse('api:resolver')

    def test_resolver_without_params_ok(self):
        data = {
            'resolver': 'core:home',
        }
        response = self.client.post(self.url, data)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_url = reverse('core:home')
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
        session = baker.make_recipe('roleplay.session', players=[self.user])
        data = {
            'resolver': 'roleplay:session:detail',
            'pk': session.pk,
        }
        response = self.client.post(self.url, data)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_url = reverse('roleplay:session:detail', kwargs={'pk': session.pk})
        url = response.json()['url']

        self.assertEqual(expected_url, url)
