from django.contrib.auth import get_user_model
from django.core import mail
from django.test import RequestFactory, TestCase
from faker import Faker
from model_bakery import baker

from registration import forms


class TestLoginForm(TestCase):
    """
    Checks if LoginForm's validations work correctly.
    """

    def setUp(self):
        self.faker = Faker()
        self.user = baker.make(get_user_model())
        # Reset password so we can control input
        password = self.faker.password()
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
        data_ko['password'] = self.faker.word()
        form = forms.SignUpForm(self.request, data=data_ko)
        self.assertFalse(form.is_valid(), 'Form is valid but it shouldn\'t.')


class TestSingUpForm(TestCase):
    """
    Checks if validations, save and everything else related to SignUpForm is working.
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
        self.discord_user = baker.make('bot.DiscordUser')
        self.request = RequestFactory().get('/')

    def test_form_ok(self):
        form = forms.SignUpForm(self.request, data=self.data_ok)
        self.assertTrue(form.is_valid(), 'Form is invalid.')

        # Adding Discord ID
        data_discord = self.data_ok.copy()
        data_discord['discord_id'] = self.discord_user.pk
        form = forms.SignUpForm(self.request, data=data_discord)
        form_valid = form.is_valid()
        self.assertTrue(form_valid, repr(form.errors))

    def test_form_wrong_confirm_password_ko(self):
        data_ko = self.data_ok.copy()
        data_ko['password2'] = self.faker.word()
        form = forms.SignUpForm(self.request, data=data_ko)
        self.assertFalse(form.is_valid(), 'Form is valid but it shouldn\'t.')

    def test_form_wrong_discord_id(self):
        data_ko = self.data_ok.copy()
        data_ko['discord_id'] = self.faker.random_int()

    def test_form_taken_email_ko(self):
        # First we create a user
        user = baker.make(get_user_model(), email=self.faker.email())
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

    def test_save_with_discord_user_ok(self):
        data_ok = self.data_ok.copy()
        data_ok['discord_id'] = self.discord_user.id
        form = forms.SignUpForm(self.request, data=data_ok)
        user = form.save()
        self.assertIsNotNone(user.discord_user, 'Discord User is not vinculed.')
        self.assertEqual(user.discord_user, self.discord_user, 'Discord User vinculed incorrectly.')

    def test_email_sent_ok(self):
        # Changing Django Settings to get email sent
        with self.settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'):
            form = forms.SignUpForm(self.request, data=self.data_ok)
            form.save()
            self.assertTrue(len(mail.outbox) == 1, 'Email aren\'t been sent.')


class TestResendEmailForm(TestCase):
    """
    Checks if user's email exists and email is sent.
    """

    def setUp(self):
        self.faker = Faker()
        self.user = baker.make(get_user_model(), email=self.faker.email())
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
        self.data_ko['email'] = self.faker.email()
        form = forms.ResendEmailForm(data=self.data_ko)
        self.assertFalse(form.is_valid(), 'Form is taken as valid but it shouldn\'t.')
