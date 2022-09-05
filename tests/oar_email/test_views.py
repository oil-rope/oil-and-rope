from django.conf import settings
from django.shortcuts import resolve_url
from django.test import TestCase, override_settings
from model_bakery import baker


class TestEmailView(TestCase):
    resolver = 'oar_email:template'

    @classmethod
    def setUpTestData(cls):
        cls.url = resolve_url(cls.resolver, mail_template='email_layout.html')
        cls.staff_user = baker.make_recipe('registration.staff_user')

    def test_anonymous_access_ko(self):
        response = self.client.get(self.url)
        login_url = resolve_url(settings.LOGIN_URL)
        expected_url = f'{login_url}?next={self.url}'

        self.assertRedirects(response, expected_url)

    def test_non_staff_access_ko(self):
        self.client.force_login(baker.make_recipe('registration.user'))
        response = self.client.get(self.url)

        self.assertEqual(403, response.status_code)

    def test_staff_access_ok(self):
        self.client.force_login(self.staff_user)
        with override_settings(DEBUG=True):
            response = self.client.get(self.url)

        self.assertEqual(200, response.status_code)

    def test_staff_access_debug_false_ko(self):
        self.client.force_login(self.staff_user)
        response = self.client.get(self.url)

        self.assertEqual(403, response.status_code)

    def test_with_json_ok(self):
        self.client.force_login(self.staff_user)
        with override_settings(DEBUG=True):
            response = self.client.get(self.url, data={'object': '{"name": "Test"}'})

        self.assertEqual(200, response.status_code)
