import datetime
import os
import pathlib
import random
import tempfile
from unittest import mock

from django.conf import settings
from django.contrib.auth import get_user, get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import resolve_url, reverse
from django.test import TestCase
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from model_bakery import baker
from PIL import Image

from common.utils.faker import create_faker
from registration.views import ActivateAccountView

fake = create_faker()


class TestLoginView(TestCase):
    """
    Checks LoginView works correctly.
    """

    resolver = 'registration:auth:login'

    def setUp(self):
        self.user = baker.make(get_user_model())
        self.url = reverse(self.resolver)

    def test_access_ok(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200, 'User cannot access view.')
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_user_can_login_ok(self):
        # Change password so we can control input
        password = fake.password()
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
        password = fake.password()
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
        password = fake.password()
        self.user.set_password(password)
        self.user.save()

        data = {
            'username': fake.email(),
            'password': password
        }
        self.assertFalse(get_user(self.client).is_authenticated, 'User is logged before post to Login.')
        self.client.post(self.url, data=data)
        self.assertFalse(get_user(self.client).is_authenticated, 'User is logged.')

    @mock.patch('registration.views.messages')
    def test_user_inactive_warning_ko(self, mock_call: mock.MagicMock):
        # Change password so we can control input
        password = fake.password()
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

        warn_message = 'Seems like this user is inactive. Have you confirmed your email?'
        mock_call.warning.assert_called_with(
            response.wsgi_request,
            warn_message
        )

    def test_invalid_credentials(self):
        """
        Since we access user on LoginView, invalid credentials should be captured by an Exception to avoid 500.
        """

        data = {
            'username': fake.user_name(),
            'password': fake.word()
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
    Checks if SignUpView works correctly.
    """

    def setUp(self):
        email = fake.safe_email()
        password = fake.password()
        self.data_ok = {
            'username': fake.user_name(),
            'email': email,
            'password1': password,
            'password2': password
        }
        self.url = reverse('registration:auth:register')

    def test_access_ok(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200, 'User cannot access view.')
        self.assertTemplateUsed(response, 'registration/register.html')

    @mock.patch('registration.views.messages')
    def test_user_can_register_ok(self, mock_call: mock.MagicMock):
        response = self.client.post(self.url, data=self.data_ok)
        success_message = 'User created! Please confirm your email.'
        mock_call.success.assert_called_with(
            response.wsgi_request,
            success_message
        )

    @mock.patch('registration.views.messages')
    def test_user_can_register_with_discord_user(self, mock_call: mock.MagicMock):
        data_ok = self.data_ok.copy()
        response = self.client.post(self.url, data=data_ok)

        success_message = 'User created! Please confirm your email.'
        mock_call.success.assert_called_with(
            response.wsgi_request,
            success_message
        )

    def test_user_is_created_ok(self):
        self.client.post(self.url, data=self.data_ok)
        user_exists = get_user_model().objects.filter(username=self.data_ok['username']).exists()
        self.assertTrue(user_exists, 'User is not created.')

    def test_email_sent_ok(self):
        # NOTE: Not necessary since for tests this backend is default
        # with self.settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'):

        self.client.post(self.url, data=self.data_ok, follow=True)
        self.assertTrue(len(mail.outbox) == 1, 'Email wasn\'t sent.')

    @mock.patch('registration.views.messages')
    def test_email_exception_ko(self, mock_call: mock.MagicMock):
        error_message = 'Seems like we are experimenting issues with our mail automatization. Please try later.'

        with self.settings(
            EMAIL_HOST='smtp.mailtrap.io', EMAIL_HOST_USER=fake.user_name(),
            EMAIL_HOST_PASSWORD=fake.password(), EMAIL_PORT=2525,
            EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend',
        ):
            response = self.client.post(self.url, data=self.data_ok, follow=True)

            mock_call.error.assert_called_with(
                response.wsgi_request,
                error_message,
            )

    def test_wrong_confirm_password(self):
        data_ko = self.data_ok.copy()
        data_ko['password2'] = fake.word()
        response = self.client.post(self.url, data=data_ko)
        self.assertFormError(response, 'form', 'password2', 'The two password fields didn’t match.')

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

    def test_discord_id_is_discriminator_ko(self):
        data_with_wrong_discord_id = self.data_ok.copy()
        data_with_wrong_discord_id['discord_id'] = f'{fake.user_name()}#1234'
        response = self.client.post(self.url, data=data_with_wrong_discord_id)
        expected_error = 'Seems like that\'s your discord discriminator not your identifier.' + \
            ' Right click on your user and then click on Copy ID.'

        self.assertFormError(response, 'form', 'discord_id', expected_error)


class TestActivateAccountView(TestCase):
    """
    Checks correct behavior for ActivateAccountView.

    We don't validate `access_ok` since a 200 code is not expected from this view.
    """

    def setUp(self):
        token_generator = PasswordResetTokenGenerator()
        self.user = baker.make(get_user_model())
        self.user.is_active = False
        self.user.save()
        self.token = token_generator.make_token(self.user)

    @mock.patch('registration.views.messages')
    def test_validates_ok(self, mock_call: mock.MagicMock):
        url = reverse('registration:auth:activate', kwargs={
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
        self.user = baker.make(get_user_model(), email=fake.email())
        self.data_ok = {
            'email': self.user.email
        }
        self.url = reverse('registration:auth:resend_email')

    def test_access_ok(self):
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code, 'User cannot access.')
        self.assertTemplateUsed(response, 'registration/resend_email.html')

    @mock.patch('registration.views.messages')
    def test_ok(self, mock_call):
        response = self.client.post(self.url, data=self.data_ok)
        self.assertEqual(302, response.status_code, 'User is no redirected.')
        success_message = 'Your confirmation email has been sent!'
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
        data_ko['email'] = fake.email()
        response = self.client.post(self.url, data=data_ko)
        self.assertFormError(response, 'form', 'email', 'This email doesn\'t belong to a user.')


class TestResetPasswordView(TestCase):

    def setUp(self):
        self.user = baker.make(get_user_model(), email=fake.email())
        self.data_ok = {
            'email': self.user.email
        }
        self.url = reverse('registration:auth:password_reset')

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
        success_message = 'Email for password reset request sent!'
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
        data_ko['email'] = fake.email()
        response = self.client.post(self.url, data=data_ko)
        self.assertFormError(response, 'form', 'email', 'This email doesn\'t belong to a user.')


class TestPasswordResetConfirmView(TestCase):

    def setUp(self):
        self.user = baker.make(get_user_model(), email=fake.email())
        self.password = 'a_p4ssw0rd@'
        self.data_ok = {
            'new_password1': self.password,
            'new_password2': self.password
        }
        self.token_generator = PasswordResetTokenGenerator()
        self.token = self.token_generator.make_token(self.user)
        self.uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.url = reverse('registration:auth:password_reset_confirm', kwargs={'uidb64': self.uid, 'token': self.token})

    def test_access_ok(self):
        response = self.client.get(self.url)
        self.assertEqual(302, response.status_code, 'User is not redirected.')

        url = response.url
        response = self.client.get(url)
        self.assertEqual(200, response.status_code, 'User cannot access.')
        self.assertTemplateUsed(response, 'registration/password_reset_confirm.html')

    @mock.patch('registration.views.messages')
    def test_ok(self, mock_call):
        response = self.client.get(self.url)
        # Decrypted URL
        url = response.url
        response = self.client.post(url, data=self.data_ok)
        self.assertEqual(302, response.status_code, 'User is no redirected.')
        success_message = 'Password changed successfully!'
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
        self.client.post(url, data=self.data_ok)

        self.client.login(
            username=self.user.username,
            password=self.password
        )

        self.assertTrue(self.user.is_authenticated, 'User cannot login with new password.')


class TestPasswordChangeView(TestCase):
    resolver = 'registration:auth:password_change'

    @classmethod
    def setUpTestData(cls):
        cls.user = baker.make_recipe('registration.user')
        cls.url = resolve_url(cls.resolver)

    def setUp(self):
        self.password = fake.password()
        self.data_ok = {
            'new_password1': self.password,
            'new_password2': self.password,
        }

    def test_anonymous_access_ko(self):
        response = self.client.get(self.url)
        login_url = resolve_url(settings.LOGIN_URL)
        expected_url = f'{login_url}?next={self.url}'

        self.assertRedirects(response, expected_url)

    def test_user_access_ok(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(200, response.status_code)

    def test_template_used_is_correct_ok(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertTemplateUsed(response, 'registration/password_change.html')

    def test_user_post_data_without_new_password1_ko(self):
        data_without_new_password1 = self.data_ok.copy()
        del data_without_new_password1['new_password1']

        self.client.force_login(self.user)
        response = self.client.post(self.url, data=data_without_new_password1)

        self.assertFormError(response, 'form', 'new_password1', ['This field is required.'])

    def test_user_post_data_without_new_password2_ko(self):
        data_without_new_password2 = self.data_ok.copy()
        del data_without_new_password2['new_password2']

        self.client.force_login(self.user)
        response = self.client.post(self.url, data=data_without_new_password2)

        self.assertFormError(response, 'form', 'new_password2', ['This field is required.'])

    def test_user_post_data_ok(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url, data=self.data_ok)

        self.assertRedirects(response, resolve_url(self.user))

    @mock.patch('registration.views.messages')
    def test_success_message_is_launched_ok(self, mocker):
        self.client.force_login(self.user)
        response = self.client.post(self.url, data=self.data_ok)

        mocker.success.assert_called_once_with(
            response.wsgi_request,
            'Password changed successfully!'
        )

    def test_user_can_login_with_new_password_ok(self):
        self.client.force_login(self.user)
        self.client.post(self.url, data=self.data_ok)

        self.client.logout()
        self.client.login(username=self.user.username, password=self.password)
        self.user.refresh_from_db()

        self.assertTrue(self.user.is_authenticated)


class TestRequestTokenView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = baker.make_recipe('registration.user')
        cls.url = reverse('registration:token')

    def test_anonymous_access_ko(self):
        login_url = reverse('registration:auth:login')
        response = self.client.get(self.url)
        expected_url = f'{login_url}?next={self.url}'

        self.assertRedirects(response, expected_url)

    def test_authenticated_access_ok(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        token = self.user.auth_token

        self.assertContains(response, f'{token.key}')


class TestUserUpdateView(TestCase):
    resolver = 'registration:user:edit'

    @classmethod
    def setUpTestData(cls):
        cls.existing_user = baker.make_recipe('registration.user')

    def setUp(self):
        self.tmp_file = tempfile.NamedTemporaryFile(mode='w', dir='./tests/', suffix='.jpg', delete=False)
        Image.new('RGB', (30, 60), color='red').save(self.tmp_file.name)
        with open(self.tmp_file.name, 'rb') as img_content:
            image = SimpleUploadedFile(name=self.tmp_file.name, content=img_content.read(), content_type='image/jpeg')

        self.user = baker.make_recipe('registration.user')
        self.url = resolve_url(self.resolver, pk=self.user.pk)
        self.data_ok = {
            'username': fake.user_name(),
            'email': fake.email(),
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'bio': fake.paragraph(),
            'birthday': fake.date_object(),
            'language': random.choice([lan[0] for lan in settings.LANGUAGES]),
            'web': fake.uri(),
            'image': image,
        }

    def tearDown(self):
        self.tmp_file.close()
        os.unlink(self.tmp_file.name)

    def test_anonymous_access_ko(self):
        login_url = resolve_url(settings.LOGIN_URL)
        response = self.client.get(self.url)
        expected_url = f'{login_url}?next={self.url}'

        self.assertRedirects(response, expected_url)

    def test_authenticated_not_user_access_ko(self):
        self.client.force_login(self.existing_user)
        response = self.client.get(self.url)

        self.assertEqual(403, response.status_code)

    def test_authenticated_user_access_ok(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(200, response.status_code)

    def test_anonymous_post_data_ko(self):
        login_url = resolve_url(settings.LOGIN_URL)
        response = self.client.post(self.url, self.data_ok)
        expected_url = f'{login_url}?next={self.url}'

        self.assertRedirects(response, expected_url)

    def test_authenticated_not_user_post_data_ko(self):
        self.client.force_login(self.existing_user)
        response = self.client.post(self.url, self.data_ok)

        self.assertEqual(403, response.status_code)

    @mock.patch('registration.views.messages')
    def test_authenticated_post_data_ok(self, mocker):
        self.client.force_login(self.user)
        response = self.client.post(self.url, self.data_ok)

        self.assertRedirects(response, self.url)
        mocker.success.assert_called_once_with(
            response.wsgi_request,
            'User updated successfully!',
        )

    def test_authenticated_user_post_data_updates_user_ok(self):
        self.client.force_login(self.user)
        self.client.post(self.url, self.data_ok)
        self.user.refresh_from_db()
        profile = self.user.profile

        self.assertEqual(self.data_ok['username'], self.user.username)
        self.assertEqual(self.data_ok['email'], self.user.email)
        self.assertEqual(self.data_ok['first_name'], self.user.first_name)
        self.assertEqual(self.data_ok['last_name'], self.user.last_name)
        self.assertEqual(self.data_ok['bio'], profile.bio)
        self.assertEqual(self.data_ok['birthday'], profile.birthday)
        self.assertEqual(self.data_ok['language'], profile.language)
        self.assertEqual(self.data_ok['web'], profile.web)

        # NOTE: Checks if image was created and stored
        image_path = pathlib.Path(settings.MEDIA_ROOT) / 'registration/profile'
        image_path /= datetime.date.today().strftime('%Y/%m/%d/') + str(profile.pk)
        image_path /= str(self.data_ok['image'])
        self.assertTrue(image_path.exists())

    def test_form_without_username_ko(self):
        self.client.force_login(self.user)
        data_without_username = self.data_ok.copy()
        del data_without_username['username']
        response = self.client.post(self.url, data_without_username)

        self.assertFormError(response, 'form', 'username', ['This field is required.'])

    def test_form_without_email_ko(self):
        self.client.force_login(self.user)
        data_without_email = self.data_ok.copy()
        del data_without_email['email']
        response = self.client.post(self.url, data_without_email)

        self.assertFormError(response, 'form', 'email', ['This field is required.'])

    def test_form_without_language_ko(self):
        self.client.force_login(self.user)
        data_without_language = self.data_ok.copy()
        del data_without_language['language']
        response = self.client.post(self.url, data_without_language)

        self.assertFormError(response, 'form', 'language', ['This field is required.'])

    @mock.patch('registration.views.messages')
    def test_form_without_image_ok(self, mocker):
        self.client.force_login(self.user)
        data_without_image = self.data_ok.copy()
        del data_without_image['image']
        response = self.client.post(self.url, data_without_image)

        self.assertRedirects(response, self.url)
        mocker.success.assert_called_once_with(
            response.wsgi_request,
            'User updated successfully!',
        )

    @mock.patch('registration.views.messages')
    def test_form_without_first_name_ok(self, mocker):
        self.client.force_login(self.user)
        data_without_first_name = self.data_ok.copy()
        del data_without_first_name['first_name']
        response = self.client.post(self.url, data_without_first_name)

        self.assertRedirects(response, self.url)
        mocker.success.assert_called_once_with(
            response.wsgi_request,
            'User updated successfully!',
        )

    @mock.patch('registration.views.messages')
    def test_form_without_last_name_ok(self, mocker):
        self.client.force_login(self.user)
        data_without_last_name = self.data_ok.copy()
        del data_without_last_name['last_name']
        response = self.client.post(self.url, data_without_last_name)

        self.assertRedirects(response, self.url)
        mocker.success.assert_called_once_with(
            response.wsgi_request,
            'User updated successfully!',
        )

    @mock.patch('registration.views.messages')
    def test_form_without_bio_ok(self, mocker):
        self.client.force_login(self.user)
        data_without_bio = self.data_ok.copy()
        del data_without_bio['bio']
        response = self.client.post(self.url, data_without_bio)

        self.assertRedirects(response, self.url)
        mocker.success.assert_called_once_with(
            response.wsgi_request,
            'User updated successfully!',
        )

    @mock.patch('registration.views.messages')
    def test_form_without_birthday_ok(self, mocker):
        self.client.force_login(self.user)
        data_without_birthday = self.data_ok.copy()
        del data_without_birthday['birthday']
        response = self.client.post(self.url, data_without_birthday)

        self.assertRedirects(response, self.url)
        mocker.success.assert_called_once_with(
            response.wsgi_request,
            'User updated successfully!',
        )

    @mock.patch('registration.views.messages')
    def test_form_without_web_ok(self, mocker):
        self.client.force_login(self.user)
        data_without_web = self.data_ok.copy()
        del data_without_web['web']
        response = self.client.post(self.url, data_without_web)

        self.assertRedirects(response, self.url)
        mocker.success.assert_called_once_with(
            response.wsgi_request,
            'User updated successfully!',
        )

    def test_form_with_existing_username_ko(self):
        self.client.force_login(self.user)
        data_with_existing_username = self.data_ok.copy()
        data_with_existing_username['username'] = self.existing_user.username
        response = self.client.post(self.url, data_with_existing_username)

        self.assertFormError(response, 'form', 'username', ['A user with that username already exists.'])

    def test_form_with_existing_email_ko(self):
        self.client.force_login(self.user)
        data_with_existing_email = self.data_ok.copy()
        data_with_existing_email['email'] = self.existing_user.email
        response = self.client.post(self.url, data_with_existing_email)

        self.assertFormError(response, 'form', 'email', ['User with this Email address already exists.'])

    def test_form_birthday_set_after_today(self):
        self.client.force_login(self.user)
        data_birthday_after_today = self.data_ok.copy()
        data_birthday_after_today['birthday'] = fake.date_between(start_date='+1d', end_date='+30d')
        response = self.client.post(self.url, data_birthday_after_today)

        self.assertFormError(response, 'form', 'birthday', ['Birthday cannot be set after today.'])
