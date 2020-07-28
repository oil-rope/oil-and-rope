import random

from django.apps import apps
from django.test import TestCase
from faker import Faker

from common.constants import models
from common.enums import AvailableIcons
from dynamic_menu import enums, forms


class TestDynamicMenuForm(TestCase):
    form_class = forms.DynamicMenuForm
    model = apps.get_model(models.DYNAMIC_MENU)

    def setUp(self):
        self.faker = Faker()
        self.icons = list(dict(AvailableIcons.choices).keys())
        self.data_ok = {
            'prepended_text': random.choice(self.icons),
            'name': self.faker.name(),
            'appended_text': random.choice(self.icons),
            'url_resolver': 'core:home',
            'permissions_required': 'auth.view_user, auth.change_user, auth.add_user',
            'related_models': 'auth.User, auth.Group',
            'staff_required': self.faker.pybool(),
            'superuser_required': self.faker.pybool(),
            'order': 0,
            'menu_type': enums.MenuTypes.MAIN_MENU
        }

    def test_data_ok(self):
        form = self.form_class(data=self.data_ok)

        self.assertTrue(form.is_valid())

    def test_data_without_prepended_text_ok(self):
        data_ko = self.data_ok.copy()
        del data_ko['prepended_text']
        form = self.form_class(data=data_ko)

        self.assertTrue(form.is_valid())

    def test_data_without_appended_text_ok(self):
        data_ko = self.data_ok.copy()
        del data_ko['appended_text']
        form = self.form_class(data=data_ko)

        self.assertTrue(form.is_valid())

    def test_data_without_url_resolver_ok(self):
        data_ko = self.data_ok.copy()
        del data_ko['url_resolver']
        form = self.form_class(data=data_ko)

        self.assertTrue(form.is_valid())

    def test_data_without_permissions_required_ok(self):
        data_ko = self.data_ok.copy()
        del data_ko['permissions_required']
        form = self.form_class(data=data_ko)

        self.assertTrue(form.is_valid())

    def test_data_without_related_models_ok(self):
        data_ko = self.data_ok.copy()
        del data_ko['related_models']
        form = self.form_class(data=data_ko)

        self.assertTrue(form.is_valid())

    def test_data_without_staff_required_ok(self):
        data_ko = self.data_ok.copy()
        del data_ko['staff_required']
        form = self.form_class(data=data_ko)

        self.assertTrue(form.is_valid())

    def test_data_without_superuser_required_ok(self):
        data_ko = self.data_ok.copy()
        del data_ko['superuser_required']
        form = self.form_class(data=data_ko)

        self.assertTrue(form.is_valid())

    def test_save_ok(self):
        form = self.form_class(data=self.data_ok)
        instance = form.save()

        self.assertTrue(self.model.objects.filter(pk=instance.pk).exists())
