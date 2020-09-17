from django.apps import apps
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase
from faker import Faker
from model_bakery import baker

from common.constants import models as constants
from dynamic_menu import context_processors
from dynamic_menu.enums import MenuTypes

Permission = apps.get_model(constants.PERMISSION_MODEL)
DynamicMenu = apps.get_model(constants.DYNAMIC_MENU)


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
            DynamicMenu.objects.create(
                name=self.faker.word(),
                menu_type=MenuTypes.MAIN_MENU
            )
        menus = context_processors.menus(self.request)

        self.assertEqual(2, len(menus['menus']))

    def test_anonymous_user_list_all_menus_ko(self):
        DynamicMenu.objects.create(
            name=self.faker.word(),
            menu_type=MenuTypes.MAIN_MENU,
            staff_required=True
        )
        count = 2
        for _ in range(0, count):
            DynamicMenu.objects.create(
                name=self.faker.word(),
                menu_type=MenuTypes.MAIN_MENU
            )
        request = RequestFactory().get('/')
        request.user = AnonymousUser()
        menus = context_processors.menus(request)

        self.assertEqual(count, len(menus['menus']))

    def test_user_with_permissions_lists_all_menus_ok(self):
        # Random menu
        DynamicMenu.objects.create(
            name=self.faker.word(),
            menu_type=MenuTypes.MAIN_MENU
        )
        # Menu with permissions
        count = 2
        for _ in range(0, count):
            menu = DynamicMenu.objects.create(
                name=self.faker.word(),
                menu_type=MenuTypes.MAIN_MENU
            )
            menu.add_permissions(*self.perms)
        menus = context_processors.menus(self.request)

        self.assertEqual(3, len(menus['menus']))

    def test_user_without_permissions_lists_all_menus_ko(self):
        # Random user
        user = baker.make(constants.USER_MODEL)
        user.user_permissions.add(
            Permission.objects.get(content_type__app_label='auth', codename='view_user')
        )
        # Random menu
        DynamicMenu.objects.create(
            name=self.faker.word(),
            menu_type=MenuTypes.MAIN_MENU
        )
        # Menu with permissions
        for _ in range(0, 2):
            menu = DynamicMenu.objects.create(
                name=self.faker.word(),
                menu_type=MenuTypes.MAIN_MENU
            )
            menu.add_permissions(*self.perms)
        request = RequestFactory().get('/')
        request.user = user
        menus = context_processors.menus(request)

        self.assertEqual(3, len(menus['menus']))

    def test_optimized_queries_ok(self):
        DynamicMenu.objects.create(
            name=self.faker.word(),
            menu_type=MenuTypes.MAIN_MENU
        )
        for _ in range(0, 3):
            menu = DynamicMenu.objects.create(
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
            'User Permissions',
            'Select all menus',
        )

        with self.assertNumQueries(len(queries)):
            context_processors.menus(request)

    def test_no_menus_ok(self):
        menus = context_processors.menus(self.request)

        self.assertEqual(0, len(menus['menus']))

    def test_context_menus_ok(self):
        menu = DynamicMenu.objects.create(
            name=self.faker.word(),
            menu_type=MenuTypes.MAIN_MENU
        )
        count = 2
        for _ in range(0, count):
            DynamicMenu.objects.create(
                name=self.faker.word(),
                menu_type=MenuTypes.CONTEXT_MENU,
                parent=menu
            )
        request = RequestFactory().get('/')
        request.user = self.user
        request.COOKIES['_auth_user_menu_referrer'] = menu.id
        menus = context_processors.menus(request)

        self.assertEqual(count, len(menus['context_menus']))
