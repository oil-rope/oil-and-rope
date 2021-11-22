from django.apps import apps
from django.shortcuts import reverse
from django.test import TestCase
from faker import Faker
from model_bakery import baker

from common.constants import models as constants
from dynamic_menu.models import DynamicMenu, dynamic_menu_path

Permission = apps.get_model(constants.PERMISSION_MODEL)
ContentType = apps.get_model(constants.CONTENT_TYPE_MODEL)


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

    def test_display_menu_name_without_extra_text_ok(self):
        expected = self.instance.name
        self.assertEqual(expected, self.instance.display_menu_name)

    def test_display_menu_name_with_extra_text_ok(self):
        prepended_text = '<i class="fa fa-user"></i>'
        self.instance.prepended_text = prepended_text
        appended_text = '<i class="fa fa-user"></i>'
        self.instance.appended_text = appended_text
        self.instance.save()
        expected = prepended_text + '  ' + self.instance.name + '  ' + appended_text
        self.assertEqual(expected, self.instance.display_menu_name)

    def test_display_menu_name_with_prepended_text_ok(self):
        prepended_text = '<i class="fa fa-user"></i>'
        self.instance.prepended_text = prepended_text
        self.instance.save()
        expected = prepended_text + '  ' + self.instance.name
        self.assertEqual(expected, self.instance.display_menu_name)

    def test_display_menu_name_with_appended_text_ok(self):
        appended_text = '<i class="fa fa-user"></i>'
        self.instance.appended_text = appended_text
        self.instance.save()
        expected = self.instance.name + '  ' + appended_text
        self.assertEqual(expected, self.instance.display_menu_name)

    def test_str_ok(self):
        expected = self.instance.name

        self.assertEqual(expected, str(self.instance))

    def test_url_property_ko(self):
        self.instance.url_resolver = 'random:random'
        self.instance.save()
        expected_url = '#no-url'
        self.assertEqual(expected_url, self.instance.url)

    def test_add_permissions_with_instances_ok(self):
        auth_permissions = Permission.objects.filter(
            content_type__app_label='registration',
            content_type__model='user'
        )
        self.instance.add_permissions(*auth_permissions)
        menu_permissions = self.instance.permissions_required.values_list('pk', flat=True)
        auth_permissions = auth_permissions.values_list('pk', flat=True)
        all_perms = all([perm in auth_permissions for perm in menu_permissions])

        self.assertTrue(all_perms)

    def test_add_permissions_with_strings_ok(self):
        perms = [
            'registration.view_user', 'registration.delete_user',
            'registration.change_user', 'registration.add_user'
        ]
        self.instance.add_permissions(*perms)
        menu_permissions = self.instance.permissions_required.values_list('pk', flat=True)
        codenames = [perm.split('.', 1)[1] for perm in perms]
        auth_permissions = Permission.objects.filter(
            content_type__app_label='registration',
            codename__in=codenames
        ).values_list('pk', flat=True)
        all_perms = all([perm in auth_permissions for perm in menu_permissions])

        self.assertTrue(all_perms)

    def test_add_permissions_mixed_ok(self):
        perms = Permission.objects.filter(
            content_type__app_label='registration',
            codename__in=['view_user', 'add_user']
        )
        self.instance.add_permissions('registration.delete_user', *perms)
        menu_permissions = self.instance.permissions_required.values_list('pk', flat=True)
        auth_permissions = Permission.objects.filter(
            content_type__app_label='registration',
            codename__in=['view_user', 'add_user', 'delete_user']
        ).values_list('pk', flat=True)
        all_perms = all([perm in auth_permissions for perm in menu_permissions])

        self.assertTrue(all_perms)

    def test_permissions_ok(self):
        perms = [
            'registration.add_user', 'registration.change_user',
            'registration.delete_user', 'registration.view_user'
        ]
        self.instance.add_permissions(*perms)
        all_perms = all([perm in perms for perm in self.instance.permissions])

        self.assertTrue(all_perms)

    def test_permissions_cached_ok(self):
        perms = [
            'registration.add_user', 'registration.change_user',
            'registration.delete_user', 'registration.view_user'
        ]
        self.instance.add_permissions(*perms)

        with self.assertNumQueries(1):
            self.instance.permissions
            all_perms = all([perm in perms for perm in self.instance.permissions])

            self.assertTrue(all_perms)
            self.assertTrue(hasattr(self.instance, '_permissions_cache'))

    def test_reset_cache_ok(self):
        self.instance.permissions
        perms = [
            'registration.add_user', 'registration.change_user',
            'registration.delete_user', 'registration.view_user'
        ]
        self.instance.add_permissions(*perms)
        all_perms = all([perm in perms for perm in self.instance.permissions])

        self.assertTrue(all_perms)
