from django.contrib.auth import get_user_model
from django.shortcuts import reverse
from django.test import TestCase
from model_bakery import baker


class TestPlaceListView(TestCase):

    def setUp(self):
        self.user = baker.make(get_user_model())
        self.url = reverse('roleplay:place_list')

    def test_access_ok(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'roleplay/place_list.html')

    def test_access_anonymous_ko(self):
        response = self.client.get(self.url)

        self.assertNotEqual(200, response.status_code)
        self.assertEqual(302, response.status_code)
