from django.test import TestCase
from model_bakery import baker
from rest_framework.test import APIRequestFactory

from api.permissions.registration import IsUserOrAdmin, IsUserProfileOrAdmin
from api.viewsets.registration import ProfileViewSet, UserViewSet


class TestIsUserProfileOrAdmin(TestCase):
    permission_class = IsUserProfileOrAdmin
    view = ProfileViewSet.as_view({'get': 'list'})

    @classmethod
    def setUpTestData(cls):
        cls.user = baker.make_recipe('registration.user')
        cls.owner = baker.make_recipe('registration.user')
        cls.obj = cls.owner.profile
        cls.admin_user = baker.make_recipe('registration.staff_user')

    def setUp(self):
        self.request = APIRequestFactory()

    def test_has_permission_ok(self):
        permission = self.permission_class()
        perm_result = permission.has_permission(self.request, self.view)

        self.assertTrue(perm_result)

    def test_has_object_permission_without_user_ko(self):
        permission = self.permission_class()
        self.request.user = None
        perm_result = permission.has_object_permission(self.request, self.view, self.obj)

        self.assertFalse(perm_result)

    def test_has_object_permission_with_admin_user_ok(self):
        permission = self.permission_class()
        self.request.user = self.admin_user
        perm_result = permission.has_object_permission(self.request, self.view, self.obj)

        self.assertTrue(perm_result)

    def test_has_object_permission_with_non_profile_owner_user_ko(self):
        permission = self.permission_class()
        self.request.user = self.user
        perm_result = permission.has_object_permission(self.request, self.view, self.obj)

        self.assertFalse(perm_result)

    def test_has_object_permission_with_profile_owner_user_ok(self):
        permission = self.permission_class()
        self.request.user = self.owner
        perm_result = permission.has_object_permission(self.request, self.view, self.obj)

        self.assertTrue(perm_result)


class TestIsUserOrAdmin(TestCase):
    permission_class = IsUserOrAdmin
    view = UserViewSet.as_view({'get': 'list'})

    @classmethod
    def setUpTestData(cls):
        cls.user = baker.make_recipe('registration.user')
        cls.owner = baker.make_recipe('registration.user')
        cls.obj = cls.owner
        cls.admin_user = baker.make_recipe('registration.staff_user')

    def setUp(self):
        self.request = APIRequestFactory()

    def test_has_permission_ok(self):
        permission = self.permission_class()
        perm_result = permission.has_permission(self.request, self.view)

        self.assertTrue(perm_result)

    def test_has_object_permission_without_user_ko(self):
        permission = self.permission_class()
        self.request.user = None
        perm_result = permission.has_object_permission(self.request, self.view, self.obj)

        self.assertFalse(perm_result)

    def test_has_object_permission_with_admin_user_ok(self):
        permission = self.permission_class()
        self.request.user = self.admin_user
        perm_result = permission.has_object_permission(self.request, self.view, self.obj)

        self.assertTrue(perm_result)

    def test_has_object_permission_with_non_profile_owner_user_ko(self):
        permission = self.permission_class()
        self.request.user = self.user
        perm_result = permission.has_object_permission(self.request, self.view, self.obj)

        self.assertFalse(perm_result)

    def test_has_object_permission_with_profile_owner_user_ok(self):
        permission = self.permission_class()
        self.request.user = self.owner
        perm_result = permission.has_object_permission(self.request, self.view, self.obj)

        self.assertTrue(perm_result)
