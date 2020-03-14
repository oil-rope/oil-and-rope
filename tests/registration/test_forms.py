from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from faker import Faker
from model_bakery import baker

from registration import forms


class TestSingUpForm(TestCase):
    """
    Checks if validations, save and everything else related to SignUpForm is working.
    """

    def setUp(self):
        self.faker = Faker()
        profile = self.faker.simple_profile()
        email = self.faker.safe_email()
        password = ''.join(self.faker.words(3))
        self.data_ok = {
            'username': profile['username'],
            'email': email,
            'password1': password,
            'password2': password
        }

    def test_form_ok(self):
        form = forms.SignUpForm(data=self.data_ok)
        self.assertTrue(form.is_valid(), 'Form is invalid.\nErrors: {errors}'.format(
            errors=', '.join([str(k) + ':' + str(v) for k, v in form.errors])
        ))

    def test_save_ok(self):
        form = forms.SignUpForm(data=self.data_ok)
        instance = form.save()
        self.assertFalse(instance.is_active, 'User is active before activating email.')
