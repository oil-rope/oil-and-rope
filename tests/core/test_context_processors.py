from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from model_bakery import baker


class TestLanguageContextProcessor(TestCase):

    def setUp(self):
        self.spanish_user = baker.make(get_user_model())
        self.spanish_profile = self.spanish_user.profile
        self.spanish_profile.language = 'es'
        self.spanish_profile.save()
        self.english_user = baker.make(get_user_model())
        self.english_profile = self.english_user.profile
        self.english_profile.language = 'en'
        self.english_profile.save()
        self.languages = dict(settings.LANGUAGES).keys()
        self.url = '/'

    def test_anomymous_user_default_language_ok(self):
        response = self.client.get(self.url, follow=True)
        self.assertEqual('en', response.context['lan'])

    def test_all_languages_are_loaded_ok(self):
        response = self.client.get(self.url, follow=True)
        self.assertEqual(self.languages, response.context['languages'])

    def test_user_language_is_loaded_ok(self):
        self.client.force_login(self.spanish_user)
        response = self.client.get(self.url, follow=True)
        self.assertEqual('es', response.context['lan'])

        self.client.force_login(self.english_user)
        response = self.client.get(self.url, follow=True)
        self.assertEqual('en', response.context['lan'])
