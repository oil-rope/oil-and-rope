import random

from django.apps import apps
from django.core.exceptions import ImproperlyConfigured
from django.test import RequestFactory, TestCase
from django.views import View
from model_bakery import baker

from common.constants import models as constants
from roleplay import mixins

Group = apps.get_model(constants.AUTH_GROUP)
User = apps.get_model(constants.REGISTRATION_USER)


class TestUserInAllWithRelatedNameMixin(TestCase):
    mixin = mixins.UserInAllWithRelatedNameMixin

    @classmethod
    def setUpTestData(cls):
        class DummyView(cls.mixin, View):
            pass
        cls.view = DummyView
        cls.user = baker.make_recipe('registration.user')
        cls.url = '/{}/'.format(random.randint(1, 10))
        cls.rq = RequestFactory().get(cls.url)
        cls.rq.user = cls.user
        cls.rq.method = 'GET'

    def setUp(self):
        self.view = self.view()

    def test_related_name_attr_not_declared_ko(self):
        self.view.related_name_attr = None
        self.view.setup(self.rq)

        with self.assertRaises(NotImplementedError):
            self.view.dispatch(self.rq)

    def test_object_without_related_name_attr_ko(self):
        self.view.model = User
        self.view.setup(self.rq, pk=self.user.pk)

        with self.assertRaises(ImproperlyConfigured):
            self.view.dispatch(self.rq)

    def test_user_not_in_all_ko(self):
        group = baker.make(Group)
        self.view.model = Group
        self.view.related_name_attr = 'user_set'
        self.view.setup(self.rq, pk=group.pk)

        self.assertFalse(self.view.test_func())

    def test_use_in_all_ok(self):
        group = baker.make(Group)
        group.user_set.add(self.user)
        self.view.model = Group
        self.view.related_name_attr = 'user_set'
        self.view.setup(self.rq, pk=group.pk)

        self.assertTrue(self.view.test_func())
