from django.apps import apps
from django.shortcuts import reverse
from django.test import TestCase
from faker import Faker
from model_bakery import baker

from common.constants import models as constants
from dynamic_menu.models import DynamicMenu, dynamic_menu_path

Permission = apps.get_model(constants.PERMISSION_MODEL)


class TestDynamicMenuModel(TestCase):

    def setUp(self):
        self.faker = Faker()
        self.instance = baker.make(DynamicMenu, url_resolver='core:home')

    def test_url_property_ok(self):
        expected_url = reverse('core:home')
        self.assertEqual(expected_url, self.instance.url)

    def test_url_with_extra_urls_args_ok(self):
        extra_urls_args = '?username=' + self.faker.user_name()
        self.instance.extra_urls_args = extra_urls_args
        self.instance.save()
        expected_url = reverse('core:home') + extra_urls_args
        self.assertEqual(expected_url, self.instance.url)

    def test_dynamic_menu_path_ok(self):
        file_name = self.faker.file_name(category='image')
        expected = 'dynamic_menu/dynamic_menu/{}/{}'.format(self.instance.pk, file_name)
        result = dynamic_menu_path(self.instance, file_name)
        self.assertEqual(expected, result)

    def test_absolute_url_ok(self):
        expected_url = reverse('core:home')
        self.assertEqual(expected_url, self.instance.get_absolute_url())

    def test_str_without_extra_text_ok(self):
        expected = self.instance.name
        self.assertEqual(expected, str(self.instance))

    def test_str_with_extra_text_ok(self):
        prepended_text = '<i class="fa fa-user"></i>'
        self.instance.prepended_text = prepended_text
        appended_text = '<i class="fa fa-user"></i>'
        self.instance.appended_text = appended_text
        self.instance.save()
        expected = prepended_text + '  ' + self.instance.name + '  ' + appended_text
        self.assertEqual(expected, str(self.instance))

    def test_str_with_prepended_text_ok(self):
        prepended_text = '<i class="fa fa-user"></i>'
        self.instance.prepended_text = prepended_text
        self.instance.save()
        expected = prepended_text + '  ' + self.instance.name
        self.assertEqual(expected, str(self.instance))

    def test_str_with_appended_text_ok(self):
        appended_text = '<i class="fa fa-user"></i>'
        self.instance.appended_text = appended_text
        self.instance.save()
        expected = self.instance.name + '  ' + appended_text
        self.assertEqual(expected, str(self.instance))

    def test_url_property_ko(self):
        self.instance.url_resolver = 'random:random'
        self.instance.save()
        expected_url = '#no-url'
        self.assertEqual(expected_url, self.instance.url)

    def test_add_permissions_with_instances_ok(self):
        auth_permissions = Permission.objects.filter(
            content_type__app_label='auth',
            content_type__model='user'
        )
        self.instance.add_permissions(*auth_permissions)
        menu_permissions = self.instance.permissions_required.values_list('pk', flat=True)
        auth_permissions = auth_permissions.values_list('pk', flat=True)
        all_perms = all([perm in auth_permissions for perm in menu_permissions])

        self.assertTrue(all_perms)
