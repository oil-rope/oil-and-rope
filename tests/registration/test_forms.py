import unittest
from smtplib import SMTPException

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import RequestFactory, TestCase
from model_bakery import baker

from common.utils import create_faker
from registration import forms

from ..bot.helpers.constants import (ANOTHER_BOT_TOKEN, LITECORD_API_URL, LITECORD_TOKEN, USER_WITH_DIFFERENT_SERVER,
                                     USER_WITH_SAME_SERVER)
from ..utils import check_litecord_connection

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
        self.request = RequestFactory().get('/')

    def test_form_ok(self):
        form = forms.SignUpForm(self.request, data=self.data_ok)
        self.assertTrue(form.is_valid(), 'Form is invalid.')

    @unittest.skipIf(not check_litecord_connection(), 'Litecord is unreachable.')
    def test_discord_id_does_not_exist_ko(self):
        data = self.data_ok.copy()
        data['discord_id'] = USER_WITH_DIFFERENT_SERVER

        with self.settings(DISCORD_API_URL=LITECORD_API_URL, BOT_TOKEN=ANOTHER_BOT_TOKEN):
            form = forms.SignUpForm(self.request, data=data)
            self.assertFalse(form.is_valid())

    @unittest.skipIf(not check_litecord_connection(), 'Litecord is unreachable.')
    def test_discord_id_exists_ok(self):
        data = self.data_ok.copy()
        data['discord_id'] = USER_WITH_SAME_SERVER

        with self.settings(DISCORD_API_URL=LITECORD_API_URL, BOT_TOKEN=LITECORD_TOKEN):
            form = forms.SignUpForm(self.request, data=data)
            self.assertTrue(form.is_valid())

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
