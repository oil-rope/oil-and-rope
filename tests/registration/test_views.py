from unittest import mock

from django.contrib.auth import get_user, get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core import mail
from django.shortcuts import reverse
from django.test import TestCase
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _
from faker import Faker
from model_bakery import baker

from registration.views import ActivateAccountView


class TestLoginView(TestCase):
    """
    Checks LoginView works correctly.
    """

    faker = Faker()
    resolver = 'registration:login'

    def setUp(self):
        self.user = baker.make(get_user_model())
        self.url = reverse(self.resolver)

    def test_access_ok(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200, 'User cannot access view.')
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_user_can_login_ok(self):
        # Change password so we can control input
        password = self.faker.password()
        self.user.set_password(password)
        self.user.save()
        data = {
            'username': self.user.username,
            'password': password
        }

        self.assertFalse(get_user(self.client).is_authenticated, 'User is logged before post to Login.')
        self.client.post(self.url, data=data)
        self.assertTrue(get_user(self.client).is_authenticated, 'User is not logged.')

    def test_user_login_with_email_ok(self):
        # Change password so we can control input
        password = self.faker.password()
        self.user.set_password(password)
        self.user.save()

        data = {
            'username': self.user.email,
            'password': password
        }
        self.assertFalse(get_user(self.client).is_authenticated, 'User is logged before post to Login.')
        self.client.post(self.url, data=data)
        self.assertTrue(get_user(self.client).is_authenticated, 'User is not logged.')

    def test_user_login_with_email_ko(self):
        # Change password so we can control input
        password = self.faker.password()
        self.user.set_password(password)
        self.user.save()

        data = {
            'username': self.faker.email(),
            'password': password
        }
        self.assertFalse(get_user(self.client).is_authenticated, 'User is logged before post to Login.')
        self.client.post(self.url, data=data)
        self.assertFalse(get_user(self.client).is_authenticated, 'User is logged.')

    @mock.patch('registration.views.messages')
    def test_user_inactive_warning_ko(self, mock_call: mock.MagicMock):
        # Change password so we can control input
        password = self.faker.password()
        self.user.set_password(password)
        # Set user as inactive
        self.user.is_active = False
        self.user.save()
        data = {
            'username': self.user.username,
            'password': password
        }

        self.assertFalse(get_user(self.client).is_authenticated, 'User is logged before post to Login.')
        response = self.client.post(self.url, data=data)
        self.assertFalse(get_user(self.client).is_authenticated, 'Inactive user is logged.')

        warn_message = '{}. {}'.format(
            _('Seems like this user is inactive'),
            _('Have you confirmed your email?')
        )
        mock_call.warning.assert_called_with(
            response.wsgi_request,
            warn_message
        )

    def test_invalid_credentials(self):
        """
        Since we access user on LoginView, invalid credentials should be captured by an Exception to avoid 500.
        """

        data = {
            'username': self.faker.user_name(),
            'password': self.faker.word()
        }
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, 200, 'Request gives {status}.'.format(
            status=response.status_code
        ))

    def test_cannot_access_if_user_is_logged(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302, 'User is not redirected.')


class TestSignUpView(TestCase):
    """
    Checks if SignUpview works correctly.
    """

    def setUp(self):
        self.faker = Faker()
        email = self.faker.safe_email()
        password = self.faker.password()
        self.data_ok = {
            'username': self.faker.user_name(),
            'email': email,
            'password1': password,
            'password2': password
        }
        self.url = reverse('registration:register')
        self.discord_user = baker.make('bot.DiscordUser')

    def test_access_ok(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200, 'User cannot access view.')
        self.assertTemplateUsed(response, 'registration/register.html')

    @mock.patch('registration.views.messages')
    def test_user_can_register_ok(self, mock_call: mock.MagicMock):
        response = self.client.post(self.url, data=self.data_ok)
        success_message = '{}! {}.'.format(
            _('User created'),
            _('Please confirm your email')
        )
        mock_call.success.assert_called_with(
            response.wsgi_request,
            success_message
        )

    @mock.patch('registration.views.messages')
    def test_user_can_register_with_discord_user(self, mock_call: mock.MagicMock):
        data_ok = self.data_ok.copy()
        data_ok['discord_id'] = self.discord_user.id
        response = self.client.post(self.url, data=data_ok)

        succes_message = '{} {}.'.format(
            _('User created!'),
            _('Please confirm your email')
        )
        mock_call.success.assert_called_with(
            response.wsgi_request,
            succes_message
        )

    def test_user_is_created_ok(self):
        self.client.post(self.url, data=self.data_ok)
        user_exists = get_user_model().objects.filter(username=self.data_ok['username']).exists()
        self.assertTrue(user_exists, 'User is not created.')

    def test_user_is_vinculed_to_discord_user(self):
        data_ok = self.data_ok.copy()
        data_ok['discord_id'] = self.discord_user.id
        self.client.post(self.url, data=data_ok)

        user = get_user_model().objects.get(username=data_ok['username'])
        self.assertIsNotNone(user.discord_user, 'Discord User is not vinculed.')
        self.assertEqual(user.discord_user, self.discord_user, 'Discord User vinculed incorrectly.')

    def test_email_sent_ok(self):
        with self.settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'):
            self.client.post(self.url, data=self.data_ok, follow=True)
            self.assertTrue(len(mail.outbox) == 1, 'Email wasn\'t sent.')

    def test_wrong_confirm_password(self):
        data_ko = self.data_ok.copy()
        data_ko['password2'] = self.faker.word()
        response = self.client.post(self.url, data=data_ko)
        self.assertFormError(response, 'form', 'password2', 'The two password fields didn’t match.')

    def test_wrong_discord_id_ko(self):
        data_ko = self.data_ok.copy()
        data_ko['discord_id'] = self.faker.random_int()
        response = self.client.post(self.url, data=data_ko)
        self.assertFormError(response, 'form', 'discord_id', 'User not found. Have you requested invitation?')

    def test_email_already_in_use(self):
        # First we create a user
        user = baker.make(get_user_model(), email=self.faker.email())
        data_ko = self.data_ok.copy()
        data_ko['email'] = user.email
        response = self.client.post(self.url, data=data_ko)
        self.assertFormError(response, 'form', 'email', 'This email is already in use.')

    def test_required_fields_not_given(self):
        data_without_email = self.data_ok.copy()
        del data_without_email['email']
        response = self.client.post(self.url, data=data_without_email)
        self.assertFormError(response, 'form', 'email', 'This field is required.')

        data_without_username = self.data_ok.copy()
        del data_without_username['username']
        response = self.client.post(self.url, data=data_without_username)
        self.assertFormError(response, 'form', 'username', 'This field is required.')

        data_without_password1 = self.data_ok.copy()
        del data_without_password1['password1']
        response = self.client.post(self.url, data=data_without_password1)
        self.assertFormError(response, 'form', 'password1', 'This field is required.')

        data_without_password2 = self.data_ok.copy()
        del data_without_password2['password2']
        response = self.client.post(self.url, data=data_without_password2)
        self.assertFormError(response, 'form', 'password2', 'This field is required.')

    def test_cannot_access_if_user_is_logged(self):
        user = baker.make(get_user_model())
        self.client.force_login(user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302, 'User is not redirected.')


class TestActivateAccountView(TestCase):
    """
    Checks correct behaviour for ActivateAccountView.

    We don't validate `access_ok` since a 200 code is not expected from this view.
    """

    def setUp(self):
        self.faker = Faker()
        token_generator = PasswordResetTokenGenerator()
        self.user = baker.make(get_user_model())
        self.user.is_active = False
        self.user.save()
        self.token = token_generator.make_token(self.user)

    @mock.patch('registration.views.messages')
    def test_validates_ok(self, mock_call: mock.MagicMock):
        url = reverse('registration:activate', kwargs={
            'token': self.token,
            'pk': self.user.pk
        })
        response = self.client.get(url)
        self.assertRedirects(response, ActivateAccountView.url)
        mock_call.success.assert_called_with(
            response.wsgi_request,
            'Your email has been confirmed!'
        )
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active, 'User is not active.')


class TestResendConfirmationEmailView(TestCase):
    """
    Checks that errors are sent, email is sent and success message displays correctly.
    """

    def setUp(self):
        self.faker = Faker()
        self.user = baker.make(get_user_model(), email=self.faker.email())
        self.data_ok = {
            'email': self.user.email
        }
        self.url = reverse('registration:resend_email')

    def test_access_ok(self):
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code, 'User cannot access.')
        self.assertTemplateUsed(response, 'registration/resend_email.html')

    @mock.patch('registration.views.messages')
    def test_ok(self, mock_call):
        response = self.client.post(self.url, data=self.data_ok)
        self.assertEqual(302, response.status_code, 'User is no redirected.')
        success_message = _('Your confirmation email has been sent') + '!'
        mock_call.success.assert_called_with(
            response.wsgi_request,
            success_message
        )

    def test_email_sent_ok(self):
        # Changing Django Settings to get email sent
        with self.settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'):
            self.client.post(self.url, data=self.data_ok)
            self.assertTrue(len(mail.outbox) == 1, 'Email aren\'t been sent.')

    def test_required_fields_not_given_ko(self):
        data_without_email = self.data_ok.copy()
        del data_without_email['email']
        response = self.client.post(self.url, data=data_without_email)
        self.assertFormError(response, 'form', 'email', 'This field is required.')

    def test_email_does_not_exists_ko(self):
        data_ko = self.data_ok.copy()
        data_ko['email'] = self.faker.email()
        response = self.client.post(self.url, data=data_ko)
        self.assertFormError(response, 'form', 'email', 'This email doesn\'t belong to a user.')


class TestResetPasswordView(TestCase):

    def setUp(self):
        self.faker = Faker()
        self.user = baker.make(get_user_model(), email=self.faker.email())
        self.data_ok = {
            'email': self.user.email
        }
        self.url = reverse('registration:password_reset')

    def test_access_ok(self):
        response = self.client.get(self.url)

        self.assertEqual(200, response.status_code, 'User cannot access.')
        self.assertTemplateUsed(response, 'registration/password_reset.html')

    def test_email_sent_ok(self):
        # Changing Django Settings to get email sent
        with self.settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'):
            self.client.post(self.url, data=self.data_ok)
            self.assertEqual(1, len(mail.outbox), 'Email aren\'t been sent.')

    @mock.patch('registration.views.messages')
    def test_ok(self, mock_call):
        response = self.client.post(self.url, data=self.data_ok)
        self.assertEqual(302, response.status_code, 'User is no redirected.')
        success_message = _('Email for password reset request sent!')
        mock_call.success.assert_called_with(
            response.wsgi_request,
            success_message
        )

    def test_required_fields_not_given_ko(self):
        data_without_email = self.data_ok.copy()
        del data_without_email['email']
        response = self.client.post(self.url, data=data_without_email)
        self.assertFormError(response, 'form', 'email', 'This field is required.')

    def test_email_does_not_exists_ko(self):
        data_ko = self.data_ok.copy()
        data_ko['email'] = self.faker.email()
        response = self.client.post(self.url, data=data_ko)
        self.assertFormError(response, 'form', 'email', 'This email doesn\'t belong to a user.')


class TestPasswordResetConfirmView(TestCase):

    def setUp(self):
        self.faker = Faker()
        self.user = baker.make(get_user_model(), email=self.faker.email())
        self.password = 'a_p4ssw0rd@'
        self.data_ok = {
            'new_password1': self.password,
            'new_password2': self.password
        }
        self.token_generator = PasswordResetTokenGenerator()
        self.token = self.token_generator.make_token(self.user)
        self.uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.url = reverse('registration:password_reset_confirm', kwargs={'uidb64': self.uid, 'token': self.token})

    def test_access_ok(self):
        response = self.client.get(self.url)
        self.assertEqual(302, response.status_code, 'User is not redirected.')

        url = response.url
        response = self.client.get(url)
        self.assertEqual(200, response.status_code, 'User cannot access.')
        self.assertTemplateUsed(response, 'registration/password_change.html')

    @mock.patch('registration.views.messages')
    def test_ok(self, mock_call):
        response = self.client.get(self.url)
        # Unencrypted URL
        url = response.url
        response = self.client.post(url, data=self.data_ok)
        self.assertEqual(302, response.status_code, 'User is no redirected.')
        success_message = _('Password changed successfully!')
        mock_call.success.assert_called_with(
            response.wsgi_request,
            success_message
        )

    def test_required_fields_not_given_ko(self):
        response = self.client.get(self.url)
        url = response.url

        data_without_new_password1 = self.data_ok.copy()
        del data_without_new_password1['new_password1']
        response = self.client.post(url, data=data_without_new_password1, follow=True)
        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertFormError(response, 'form', 'new_password1', 'This field is required.')

        data_without_new_password2 = self.data_ok.copy()
        del data_without_new_password2['new_password2']
        response = self.client.post(url, data=data_without_new_password2, follow=True)
        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertFormError(response, 'form', 'new_password2', 'This field is required.')

    def test_user_can_login_with_new_password_ok(self):
        response = self.client.get(self.url)
        # Encrypted URL
        url = response.url
        response = self.client.post(url, data=self.data_ok)

        self.client.login(
            username=self.user.username,
            password=self.password
        )

        self.assertTrue(self.user.is_authenticated, 'User cannot login with new password.')
