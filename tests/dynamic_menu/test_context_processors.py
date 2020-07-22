from django.apps import apps
from django.test import RequestFactory, TestCase
from faker import Faker
from model_bakery import baker

from common.constants import models as constants
from dynamic_menu import context_processors, models
from dynamic_menu.enums import MenuTypes

Permission = apps.get_model(constants.PERMISSION_MODEL)


class TestMenuContextProcessor(TestCase):

    def setUp(self):
        self.faker = Faker()
        self.user = baker.make(constants.USER_MODEL)
        self.request = RequestFactory().get('/')
        self.request.user = self.user
        self.perms = Permission.objects.filter(
            content_type__app_label='auth',
            codename__in=['view_user', 'delete_user']
        )
        self.user.user_permissions.add(*self.perms)

    def test_context_processor_exists_ok(self):
        count = 2
        for _ in range(0, count):
            models.DynamicMenu.objects.create(
                name=self.faker.word(),
                menu_type=MenuTypes.MAIN_MENU
            )
        menus = context_processors.menus(self.request)

        self.assertEqual(2, menus['menus'].count())

    def test_user_with_permissions_lists_all_menus_ok(self):
        # Random menu
        models.DynamicMenu.objects.create(
            name=self.faker.word(),
            menu_type=MenuTypes.MAIN_MENU
        )
        # Menu with permissions
        count = 2
        for _ in range(0, count):
            menu = models.DynamicMenu.objects.create(
                name=self.faker.word(),
                menu_type=MenuTypes.MAIN_MENU
            )
            menu.add_permissions(*self.perms)
        menus = context_processors.menus(self.request)

        self.assertEqual(3, menus['menus'].count())

    def test_user_without_permissions_lists_all_menus_ko(self):
        # Random user
        user = baker.make(constants.USER_MODEL)
        user.user_permissions.add(
            Permission.objects.get(content_type__app_label='auth', codename='view_user')
        )
        # Random menu
        models.DynamicMenu.objects.create(
            name=self.faker.word(),
            menu_type=MenuTypes.MAIN_MENU
        )
        # Menu with permissions
        for _ in range(0, 2):
            menu = models.DynamicMenu.objects.create(
                name=self.faker.word(),
                menu_type=MenuTypes.MAIN_MENU
            )
            menu.add_permissions(*self.perms)
        request = RequestFactory().get('/')
        request.user = user
        menus = context_processors.menus(request)

        self.assertEqual(1, menus['menus'].count())

    def test_optimized_queries_ok(self):
        models.DynamicMenu.objects.create(
            name=self.faker.word(),
            menu_type=MenuTypes.MAIN_MENU
        )
        for _ in range(0, 3):
            menu = models.DynamicMenu.objects.create(
                name=self.faker.word(),
                menu_type=MenuTypes.MAIN_MENU
            )
            menu.add_permissions(*self.perms)
        user = baker.make(constants.USER_MODEL)
        user.user_permissions.add(
            Permission.objects.get(content_type__app_label='auth', codename='view_user')
        )
        request = RequestFactory().get('/')
        request.user = user
        queries = (
            'Menus exists',
            'User Permissions',
            'Group Permissions',
            'Select all menus',
            'First menu',
            'Second menu',
            'Third menu',
            'Fourth menu'
        )

        with self.assertNumQueries(len(queries)):
            context_processors.menus(request)
