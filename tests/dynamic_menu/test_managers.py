from django.apps import apps
from django.test import TestCase
from model_bakery import baker

from common.constants import models


class TestDynamicMenuManager(TestCase):
    model = apps.get_model(models.DYNAMIC_MENU)

    def setUp(self):
        self.user = baker.make(models.REGISTRATION_USER, is_staff=False, is_superuser=False)
        self.superuser = baker.make(models.REGISTRATION_USER, is_staff=False, is_superuser=True)
        self.menu_with_perms = baker.make(self.model)
        perms = ['registration.view_user', 'registration.add_user']
        self.menu_with_perms.add_permissions(*perms)
        self.menu_without_perms = baker.make(self.model)

    def test_from_user_non_superuser_ok(self):
        queries = (
            'SELECT user_perms',
            'SELECT group_perms',
            'SELECT menus',
        )

        with self.assertNumQueries(len(queries)):
            self.model.objects.from_user(self.user)

    def test_from_user_superuser_ok(self):
        queries = (
            'SELECT permissions',
            'SELECT menus',
        )

        with self.assertNumQueries(len(queries)):
            self.model.objects.from_user(self.superuser)

    def test_from_user_length_ok(self):
        expected_menus = 1
        menus = self.model.objects.from_user(self.user)

        self.assertEqual(expected_menus, len(menus))

    def test_from_user_superuser_length_ok(self):
        expected_menus = 2
        menus = self.model.objects.from_user(self.superuser)

        self.assertEqual(expected_menus, len(menus))
