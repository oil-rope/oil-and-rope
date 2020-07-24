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

        self.assertEqual(2, menus['menus'].count())

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

        self.assertEqual(count, menus['menus'].count())

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

        self.assertEqual(3, menus['menus'].count())

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

        self.assertEqual(1, menus['menus'].count())

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

    def test_no_menus_ok(self):
        menus = context_processors.menus(self.request)

        self.assertEqual(0, menus['menus'].count())

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

        self.assertEqual(count, menus['context_menus'].count())

    def test_non_existent_menu_parent_ko(self):
        menu = DynamicMenu.objects.create(
            name=self.faker.word(),
            menu_type=MenuTypes.MAIN_MENU
        )
        DynamicMenu.objects.create(
            name=self.faker.word(),
            menu_type=MenuTypes.CONTEXT_MENU,
            parent=menu
        )
        request = RequestFactory().get('/')
        request.user = self.user
        request.COOKIES['_auth_user_menu_referrer'] = self.faker.pyint(100, 1000)
        menus = context_processors.menus(request)

        self.assertEqual(0, menus['context_menus'].count())
        self.assertIsNone(request.COOKIES['_auth_user_menu_referrer'])


class TestFilterMenus(TestCase):

    def setUp(self):
        self.faker = Faker()
        self.auth_permssions = ['add_user', 'add_group', 'delete_user', 'delete_group']
        self.auth_permssions = Permission.objects.filter(
            content_type__app_label='auth', codename__in=self.auth_permssions
        )
        self.user = baker.make(constants.USER_MODEL)
        self.staff_user = baker.make(constants.USER_MODEL, is_staff=True)
        self.superuser = baker.make(constants.USER_MODEL, is_superuser=True)
        self.user_with_perms = baker.make(constants.USER_MODEL)
        self.user_with_perms.user_permissions.add(*self.auth_permssions)

        self.menu_without_perms = DynamicMenu.objects.create(name=self.faker.word())
        self.menu_with_auth_perms = DynamicMenu.objects.create(name=self.faker.word())
        self.menu_with_auth_perms.add_permissions(*self.auth_permssions)
        self.menu_with_staff = DynamicMenu.objects.create(name=self.faker.word(), staff_required=True)
        self.menu_with_superuser = DynamicMenu.objects.create(name=self.faker.word(), superuser_required=True)

        self.menus = DynamicMenu.objects.all()

    def test_menu_without_perms_ok(self):
        menus = context_processors.filter_menus(self.menus, self.user)

        self.assertIn(self.menu_without_perms, menus)

    def test_user_without_perms_ok(self):
        menus = context_processors.filter_menus(self.menus, self.user)

        self.assertIn(self.menu_without_perms, menus)
        self.assertNotIn(self.menu_with_auth_perms, menus)

    def test_non_staff_user_ok(self):
        menus = context_processors.filter_menus(self.menus, self.user)

        self.assertIn(self.menu_without_perms, menus)
        self.assertNotIn(self.menu_with_staff, menus)

    def test_non_superuser_user_ok(self):
        menus = context_processors.filter_menus(self.menus, self.user)

        self.assertIn(self.menu_without_perms, menus)
        self.assertNotIn(self.menu_with_superuser, menus)
