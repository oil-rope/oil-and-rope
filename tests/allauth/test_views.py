from allauth.socialaccount.models import SocialAccount
from django.conf import settings
from django.shortcuts import resolve_url
from django.test import TestCase
from model_bakery import baker


class TestAllauth(TestCase):
    """
    Test overridden functionality of allauth.
    """

    login_url = resolve_url(settings.LOGIN_URL)
    social_account_google_login_url = resolve_url('google_login')
    social_account_connections_url = resolve_url('socialaccount_connections')
    social_account_login_template_name = 'socialaccount/login.html'
    social_account_connections_template_name = 'socialaccount/connections.html'

    @classmethod
    def setUpTestData(cls):
        cls.user = baker.make_recipe('registration.user')

    def test_anonymous_access_allauth_google_login_login_ok(self):
        response = self.client.get(self.social_account_google_login_url)

        self.assertEqual(200, response.status_code)

    def test_anonymous_access_allauth_google_login_templated_used_is_correct(self):
        response = self.client.get(self.social_account_google_login_url)

        self.assertTemplateUsed(response, self.social_account_login_template_name)

    def test_authenticated_user_access_allauth_google_login_ok(self):
        self.client.force_login(self.user)
        response = self.client.get(self.social_account_google_login_url)

        self.assertEqual(200, response.status_code)

    def test_authenticated_user_access_allauth_google_login_templated_used_is_correct(self):
        self.client.force_login(self.user)
        response = self.client.get(self.social_account_google_login_url)

        self.assertTemplateUsed(response, self.social_account_login_template_name)

    def test_authenticated_user_access_allauth_google_login_with_process_connect_ok(self):
        self.client.force_login(self.user)
        response = self.client.get(self.social_account_google_login_url, {'process': 'connect'})

        self.assertEqual(200, response.status_code)

    def test_anonymous_access_allauth_social_account_connections_ko(self):
        response = self.client.get(self.social_account_connections_url)
        expected_url = f'{self.login_url}?next={self.social_account_connections_url}'

        self.assertRedirects(response, expected_url)

    def test_authenticated_user_access_allauth_social_account_connections_ok(self):
        self.client.force_login(self.user)
        response = self.client.get(self.social_account_connections_url)

        self.assertEqual(200, response.status_code)

    def test_authenticated_user_access_allauth_social_account_connections_templated_used_is_correct(self):
        self.client.force_login(self.user)
        response = self.client.get(self.social_account_connections_url)

        self.assertTemplateUsed(response, self.social_account_connections_template_name)

    def test_authenticated_user_access_allauth_social_account_connections_with_form_accounts_ok(self):
        user = baker.make_recipe('registration.user')
        baker.make(SocialAccount, user=user, provider='google')
        self.client.force_login(user)
        response = self.client.get(self.social_account_connections_url)

        self.assertEqual(200, response.status_code)
