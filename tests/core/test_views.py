from django.shortcuts import reverse
from django.test import TestCase


class TestIndexView(TestCase):

    def setUp(self):
        self.url = reverse('core:index')

    def test_access_ok(self):
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code, 'User cannot access. Got %s' % response.status_code)
        self.assertTemplateUsed(response, 'core/index.html')
