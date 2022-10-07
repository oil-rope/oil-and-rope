import os
import random
import tempfile
from smtplib import SMTPException
from unittest.mock import MagicMock, patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TestCase
from model_bakery import baker
from PIL import Image

from common.utils import create_faker
from registration import forms
from tests.mocks import discord

fake = create_faker()


class TestLoginForm(TestCase):
    """
    Checks if LoginForm's validations work correctly.
    """

    def setUp(self):
        self.user = baker.make(get_user_model())
        # Reset password so we can control input
        password = fake.password()
        self.user.set_password(password)
        self.user.save()
        self.data_ok = {
            'username': self.user.username,
            'password': password
        }
        self.request = RequestFactory().get('/')

    def test_form_ok(self):
        form = forms.LoginForm(data=self.data_ok)
        self.assertTrue(form.is_valid(), 'Form is invalid.')

    def test_form_invalid_password_ko(self):
        data_ko = self.data_ok.copy()
        data_ko['password'] = fake.word()
        form = forms.SignUpForm(self.request, data=data_ko)
        self.assertFalse(form.is_valid(), 'Form is valid but it shouldn\'t.')


class TestSignUpForm(TestCase):
    """
    Checks if validations, save and everything else related to SignUpForm is working.
    """

    def setUp(self):
        email = fake.safe_email()
        password = fake.password()
        self.data_ok = {
            'username': fake.user_name(),
            'email': email,
            'password1': password,
            'password2': password,
        }

        request = self.client.get('/').wsgi_request
        self.request = request

    def test_form_ok(self):
        form = forms.SignUpForm(self.request, data=self.data_ok)
        self.assertTrue(form.is_valid(), 'Form is invalid.')

    @patch('bot.utils.discord_api_request')
    def test_discord_id_exists_ok(self, mocker_discord_request: MagicMock):
        discord_id = f'{fake.random_number(digits=18)}'
        mocker_discord_request.return_value = discord.user_response(id=discord_id)
        data = self.data_ok.copy()
        data['discord_id'] = discord_id

        form = forms.SignUpForm(self.request, data=data)
        self.assertTrue(form.is_valid())

    def test_discord_id_is_discriminator_ko(self):
        data = self.data_ok.copy()
        data['discord_id'] = f'{fake.user_name()}#1234'
        form = forms.SignUpForm(self.request, data=data)

        self.assertFalse(form.is_valid())

    def test_form_wrong_confirm_password_ko(self):
        data_ko = self.data_ok.copy()
        data_ko['password2'] = fake.word()
        form = forms.SignUpForm(self.request, data=data_ko)
        self.assertFalse(form.is_valid(), 'Form is valid but it shouldn\'t.')

    def test_form_taken_email_ko(self):
        # First we create a user
        user = baker.make(get_user_model(), email=fake.email())
        data_ko = self.data_ok.copy()
        data_ko['email'] = user.email
        form = forms.SignUpForm(self.request, data=data_ko)
        self.assertFalse(form.is_valid(), 'Form is valid but it shouldn\'t.')

    def test_required_fields_not_supplied_ko(self):
        data_without_email = self.data_ok.copy()
        del data_without_email['email']
        form = forms.SignUpForm(self.request, data=data_without_email)
        self.assertFalse(form.is_valid(), 'Form is valid but it shouldn\'t.')

        data_without_username = self.data_ok.copy()
        del data_without_username['username']
        form = forms.SignUpForm(self.request, data=data_without_username)
        self.assertFalse(form.is_valid(), 'Form is valid but it shouldn\'t.')

        data_without_password1 = self.data_ok.copy()
        del data_without_password1['password1']
        form = forms.SignUpForm(self.request, data=data_without_password1)
        self.assertFalse(form.is_valid(), 'Form is valid but it shouldn\'t.')

        data_without_password2 = self.data_ok.copy()
        del data_without_password2['password2']
        form = forms.SignUpForm(self.request, data=data_without_password2)
        self.assertFalse(form.is_valid(), 'Form is valid but it shouldn\'t.')

    def test_save_ok(self):
        form = forms.SignUpForm(self.request, data=self.data_ok)
        user = form.save()
        self.assertFalse(user.is_active, 'User is active before activating email.')

    def test_email_sent_ok(self):
        # NOTE: Not necessary anymore since it does it by default
        # Changing Django Settings to get email sent
        # with self.settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'):

        form = forms.SignUpForm(self.request, data=self.data_ok)
        form.save()
        self.assertTrue(len(mail.outbox) == 1, 'Email aren\'t been sent.')

    def test_email_exception_ko(self):
        with self.settings(
            EMAIL_HOST='smtp.mailtrap.io', EMAIL_HOST_USER=fake.user_name(),
            EMAIL_HOST_PASSWORD=fake.password(), EMAIL_PORT=2525,
            EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend',
        ):
            form = forms.SignUpForm(self.request, data=self.data_ok)
            with self.assertRaises(SMTPException):
                form.save()


class TestResendEmailForm(TestCase):
    """
    Checks if user's email exists and email is sent.
    """

    def setUp(self):
        self.user = baker.make(get_user_model(), email=fake.email())
        self.data_ok = {
            'email': self.user.email
        }

    def test_form_ok(self):
        form = forms.ResendEmailForm(data=self.data_ok)
        self.assertTrue(form.is_valid(), 'Form is taken as invalid but it shouldn\'t.')

    def test_form_required_fields_are_not_supplied(self):
        self.data_ko = self.data_ok.copy()
        del self.data_ko['email']
        form = forms.ResendEmailForm(data=self.data_ko)
        self.assertFalse(form.is_valid(), 'Form is taken as valid but it shouldn\'t.')

    def test_email_does_not_exist(self):
        self.data_ko = self.data_ok.copy()
        self.data_ko['email'] = fake.email()
        form = forms.ResendEmailForm(data=self.data_ko)
        self.assertFalse(form.is_valid(), 'Form is taken as valid but it shouldn\'t.')


class TestPasswordResetForm(TestCase):
    form_class = forms.PasswordResetForm

    def setUp(self):
        self.user = baker.make(get_user_model(), email=fake.email())
        self.data_ok = {
            'email': self.user.email
        }

    def test_form_ok(self):
        form = self.form_class(data=self.data_ok)
        self.assertTrue(form.is_valid(), 'Form is taken as invalid but it shouldn\'t.')

    def test_form_required_fields_are_not_supplied(self):
        self.data_ko = self.data_ok.copy()
        del self.data_ko['email']
        form = self.form_class(data=self.data_ko)
        self.assertFalse(form.is_valid(), 'Form is taken as valid but it shouldn\'t.')

    def test_email_does_not_exist(self):
        self.data_ko = self.data_ok.copy()
        self.data_ko['email'] = fake.email()
        form = self.form_class(data=self.data_ko)
        self.assertFalse(form.is_valid(), 'Form is taken as valid but it shouldn\'t.')


class TestSetPasswordForm(TestCase):
    form_class = forms.SetPasswordForm

    def setUp(self):
        self.user = baker.make(get_user_model(), email=fake.email())
        self.password = 'a_p4ssw0rd@'
        self.data_ok = {
            'new_password1': self.password,
            'new_password2': self.password
        }

    def test_form_ok(self):
        form = self.form_class(user=self.user, data=self.data_ok)
        self.assertTrue(form.is_valid(), 'Form is taken as invalid but it shouldn\'t.')

    def test_wrong_confirm_password_ko(self):
        data_wrong_password = self.data_ok.copy()
        data_wrong_password['new_password2'] = 'random_p4ssw0rd@'
        form = self.form_class(user=self.user, data=data_wrong_password)
        self.assertFalse(form.is_valid(), 'Form is valid but it shouldn\'t.')

    def test_required_fields_not_supplied_ko(self):
        data_without_password1 = self.data_ok.copy()
        del data_without_password1['new_password1']
        form = self.form_class(user=self.user, data=data_without_password1)
        self.assertFalse(form.is_valid(), 'Form is valid but it shouldn\'t.')

        data_without_password2 = self.data_ok.copy()
        del data_without_password2['new_password2']
        form = self.form_class(user=self.user, data=data_without_password2)
        self.assertFalse(form.is_valid(), 'Form is valid but it shouldn\'t.')

    def test_password_changed_ok(self):
        form = self.form_class(user=self.user, data=self.data_ok)
        form.is_valid()
        form.save()
        self.client.login(username=self.user.username, password=self.password)

        self.assertTrue(self.user.is_authenticated, 'User cannot login with new password.')


class TestUserForm(TestCase):
    form_class = forms.UserForm

    @classmethod
    def setUpTestData(cls):
        cls.existing_user = baker.make_recipe('registration.user')

    def setUp(self):
        self.tmp_file = tempfile.NamedTemporaryFile(mode='w', dir='./tests/', suffix='.jpg', delete=False)
        Image.new('RGB', (30, 60), color='red').save(self.tmp_file.name)
        with open(self.tmp_file.name, 'rb') as img_content:
            image = SimpleUploadedFile(name=self.tmp_file.name, content=img_content.read(), content_type='image/jpeg')

        self.user = baker.make_recipe('registration.user')
        self.data_ok = {
            'username': fake.user_name(),
            'email': fake.email(),
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'bio': fake.paragraph(),
            'birthday': fake.date_object(),
            'language': random.choice([lan[0] for lan in settings.LANGUAGES]),
            'web': fake.uri(),
        }
        self.files = {
            'image': image,
        }

    def tearDown(self):
        self.tmp_file.close()
        os.unlink(self.tmp_file.name)

    def test_data_ok(self):
        form = self.form_class(data=self.data_ok, files=self.files)

        self.assertTrue(form.is_valid())

    def test_data_without_username_ko(self):
        data_without_username = self.data_ok.copy()
        del data_without_username['username']
        form = self.form_class(data=data_without_username, files=self.files)

        self.assertFalse(form.is_valid())

    def test_data_without_language_ko(self):
        data_without_language = self.data_ok.copy()
        del data_without_language['language']
        form = self.form_class(data=data_without_language, files=self.files)

        self.assertFalse(form.is_valid())

    def test_data_without_email_ko(self):
        data_without_email = self.data_ok.copy()
        del data_without_email['email']
        form = self.form_class(data=data_without_email, files=self.files)

        self.assertFalse(form.is_valid())

    def test_data_without_image_ok(self):
        form = self.form_class(data=self.data_ok)

        self.assertTrue(form.is_valid())

    def test_data_without_first_name_ok(self):
        data_without_first_name = self.data_ok.copy()
        del data_without_first_name['first_name']
        form = self.form_class(data=data_without_first_name, files=self.files)

        self.assertTrue(form.is_valid())

    def test_data_without_last_name_ok(self):
        data_without_last_name = self.data_ok.copy()
        del data_without_last_name['last_name']
        form = self.form_class(data=data_without_last_name, files=self.files)

        self.assertTrue(form.is_valid())

    def test_data_without_bio_ok(self):
        data_without_bio = self.data_ok.copy()
        del data_without_bio['bio']
        form = self.form_class(data=data_without_bio, files=self.files)

        self.assertTrue(form.is_valid())

    def test_data_without_birthday_ok(self):
        data_without_birthday = self.data_ok.copy()
        del data_without_birthday['birthday']
        form = self.form_class(data=data_without_birthday, files=self.files)

        self.assertTrue(form.is_valid())

    def test_data_without_web_ok(self):
        data_without_web = self.data_ok.copy()
        del data_without_web['web']
        form = self.form_class(data=data_without_web, files=self.files)

        self.assertTrue(form.is_valid())

    def test_data_existing_username_ko(self):
        data_existing_username = self.data_ok.copy()
        data_existing_username['username'] = self.existing_user.username
        form = self.form_class(data=data_existing_username, files=self.files)

        self.assertFalse(form.is_valid())
        self.assertTrue(form.has_error('username'))
        # NOTE: AssertIn is necessary since `form.errors` returns a list of errors for that field
        self.assertIn('A user with that username already exists.', form.errors['username'])

    def test_data_existing_email_ko(self):
        data_existing_email = self.data_ok.copy()
        data_existing_email['email'] = self.existing_user.email
        form = self.form_class(data=data_existing_email, files=self.files)

        self.assertFalse(form.is_valid())
        self.assertTrue(form.has_error('email'))
        # NOTE: AssertIn is necessary since `form.errors` returns a list of errors for that field
        self.assertIn('User with this Email address already exists.', form.errors['email'])

    def test_data_birthday_set_after_today(self):
        data_birthday_after_today = self.data_ok.copy()
        data_birthday_after_today['birthday'] = fake.date_between(start_date='+1d', end_date='+30d')
        form = self.form_class(data=data_birthday_after_today, files=self.files)

        self.assertFalse(form.is_valid())
        self.assertTrue(form.has_error('birthday'))
        # NOTE: AssertIn is necessary since `form.errors` returns a list of errors for that field
        self.assertIn('Birthday cannot be set after today.', form.errors['birthday'])

    def test_user_actually_updates_ok(self):
        form = self.form_class(data=self.data_ok, files=self.files, instance=self.user)
        form.is_valid()
        form.save()
        self.user.refresh_from_db()

        self.assertEqual(self.data_ok['username'], self.user.username)
        self.assertEqual(self.data_ok['email'], self.user.email)
        self.assertEqual(self.data_ok['first_name'], self.user.first_name)
        self.assertEqual(self.data_ok['last_name'], self.user.last_name)

    def test_user_profile_actually_updates_ok(self):
        form = self.form_class(data=self.data_ok, files=self.files, instance=self.user)
        form.is_valid()
        form.save()
        profile = self.user.profile

        self.assertEqual(self.data_ok['bio'], profile.bio)
        self.assertEqual(self.data_ok['birthday'], profile.birthday)
        self.assertEqual(self.data_ok['language'], profile.language)
        self.assertEqual(self.data_ok['web'], profile.web)
