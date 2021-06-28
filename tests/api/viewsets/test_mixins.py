from django.apps import apps
from django.core.exceptions import ImproperlyConfigured
from model_bakery import baker
from rest_framework.test import APITestCase
from rest_framework.viewsets import ReadOnlyModelViewSet

from api.viewsets.mixins import UserListMixin
from common.constants import models

User = apps.get_model(models.USER_MODEL)


class TestUserListMixin(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.mixin = UserListMixin

        cls.user = baker.make(User)

    def setUp(self):
        class DummyClass(self.mixin, ReadOnlyModelViewSet):
            queryset = User.objects.all()
        self.view = DummyClass
        self.client.force_login(self.user)

    def test_related_name_not_given_ko(self):
        wsgi_request = self.client.get('/').wsgi_request
        with self.assertRaises(ImproperlyConfigured) as ex:
            self.view.as_view({'get': 'user_list'})(wsgi_request)
            self.assertRegex(
                str(ex),
                r'.*should either include a `related_name` attribute, or override the `get_related_name` method.'
            )

    def test_related_name_does_not_exist_ko(self):
        wsgi_request = self.client.get('/').wsgi_request
        setattr(self.view, 'related_name', 'randomization')
        with self.assertRaises(AttributeError) as ex:
            self.view.as_view({'get': 'user_list'})(wsgi_request)
            self.assertRegex(
                str(ex),
                r'User doesn\'t have .* attribute.'
            )
