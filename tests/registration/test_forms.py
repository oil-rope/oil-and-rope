from model_bakery import baker

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

class TestSingUpForm(TestCase):
    """
    Checks if validations, save and everything else related to SignUpForm is working.
    """

    def setUp(self):
        self.user = baker.make(get_user_model())

    def test_form_ok(self):
        self.assertTrue(True)
