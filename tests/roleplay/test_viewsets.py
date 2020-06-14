from django.contrib.auth import get_user_model
from django.shortcuts import reverse
from django.test import TestCase
from model_bakery import baker
from rest_framework.test import APIClient

from roleplay import models


class TestPlaceViewSet(TestCase):
    model = models.Place

    def setUp(self):
        self.client = APIClient()
        self.user = baker.make(get_user_model())
        self.world = baker.make(self.model)
        self.url = reverse('roleplay:place-list')

    def test_access_ok(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code, 'User cannot access.')

    def test_anonymous_user_ko(self):
        response = self.client.get(self.url)
        self.assertEqual(403, response.status_code, 'Anonymous user can access.')

    def test_post_request_ko(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url)
        self.assertEqual(403, response.status_code, 'User can make post request.')
        msg = 'You do not have permission to perform this action.'
        self.assertEqual(msg, response.json()['detail'], 'Message is incorrect.')
