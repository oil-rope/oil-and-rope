from django.contrib.auth import get_user_model
from django.shortcuts import reverse
from django.test import TestCase
from model_bakery import baker


class TestLoginView(TestCase):
    """
    Checks LoginView works correctly.
    """

    def test_access_ok(self):
        response = self.client.get(reverse('registration:login'))
        self.assertEqual(response.status_code, 200, 'User cannot access view.')
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_cannot_access_login_page_when_logged(self):
        user = baker.make(get_user_model())
        self.client.force_login(user)
        response = self.client.get(reverse('registration:login'))
        self.assertEqual(response.status_code, 302, 'User is not redirected.')


class TestSignUpView(TestCase):
    """
    Checks if SignUpview works correctly.
    """

    def test_access_ok(self):
        response = self.client.get(reverse('registration:register'))
        self.assertEqual(response.status_code, 200, 'User cannot access view.')
        self.assertTemplateUsed(response, 'registration/register.html')
