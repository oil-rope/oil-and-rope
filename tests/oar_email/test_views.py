from django.conf import settings
from django.shortcuts import resolve_url
from django.test import TestCase
from model_bakery import baker


class TestEmailView(TestCase):
    resolver = 'oar_email:template'

    def test_anonymous_access_ko(self):
        url = resolve_url(self.resolver, mail_template='email_layout.html')
        response = self.client.get(url)
        login_url = resolve_url(settings.LOGIN_URL)
        expected_url = f'{login_url}?next={url}'

        self.assertRedirects(response, expected_url)

    def test_non_staff_access_ko(self):
        self.client.force_login(baker.make_recipe('registration.user'))
        url = resolve_url(self.resolver, mail_template='email_layout.html')
        response = self.client.get(url)

        self.assertNotEqual(200, response.status_code)

    def test_staff_access_ok(self):
        self.client.force_login(baker.make_recipe('registration.staff_user'))
        url = resolve_url(self.resolver, mail_template='email_layout.html')
        response = self.client.get(url)

        self.assertEqual(200, response.status_code)
