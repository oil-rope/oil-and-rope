from http.cookies import SimpleCookie

from django.conf import settings
from django.shortcuts import resolve_url
from django.test import Client, TestCase

from tests.utils import fake


class CSRFFailureViewTestCase(TestCase):
    csrftoken = 'kf2CdCaoRHFnvhYZBJzjzLBuKzLT75D3'  # Random token got from a GET request
    template = '403_csrf.html'
    url = resolve_url(settings.LOGIN_URL)

    def setUp(self) -> None:
        self.client = Client(enforce_csrf_checks=True)
        self.data = {
            'username': fake.user_name(),
            'password': fake.password(),
        }

    def test_missing_xcsrftoken_header_ko(self):
        self.client.cookies = SimpleCookie({'csrftoken': self.csrftoken})
        response = self.client.post(self.url, self.data)

        self.assertEqual(403, response.status_code)
        self.assertTemplateUsed(response, self.template)
        self.assertContains(response, 'CSRF token missing.', status_code=403)

    def test_missing_csrftoken_cookie_ko(self):
        response = self.client.post(self.url, self.data, HTTP_X_CSRFTOKEN=self.csrftoken)

        self.assertEqual(403, response.status_code)
        self.assertTemplateUsed(response, self.template)
        self.assertContains(response, 'this site requires a CSRF cookie', status_code=403)
