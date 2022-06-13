import random

from django.core.exceptions import ImproperlyConfigured
from django.test import RequestFactory, TestCase
from django.views import View
from django.views.generic.detail import SingleObjectMixin
from model_bakery import baker

from common import mixins


class TestOwnerRequiredMixin(TestCase):
    mixin = mixins.OwnerRequiredMixin

    @classmethod
    def setUpTestData(cls):
        class TestView(cls.mixin, SingleObjectMixin, View):
            pass
        cls.view = TestView

    def setUp(self):
        self.user = baker.make_recipe('registration.user')
        self.url = '/{}/'.format(random.randint(1, 10))
        self.rq = RequestFactory().get(self.url)
        self.rq.method = 'GET'
        self.view = self.view()

    def test_dispatch_not_owner_attr(self):
        self.rq.user = self.user
        view = self.view
        view.owner_attr = None
        view.setup(self.rq)

        with self.assertRaises(ImproperlyConfigured) as ex:
            view.test_func()
        exception = ex.exception
        self.assertEqual(str(exception), 'OwnerRequiredMixin requires a definition of \'owner_attr\'.')

    def test_user_not_owner_ko(self):
        self.rq.user = self.user
        view = self.view
        view.get_object = lambda: baker.make_recipe('roleplay.world')
        view.setup(self.rq)

        self.assertFalse(view.test_func())

    def test_user_is_owner_ok(self):
        self.rq.user = self.user
        view = self.view
        view.get_object = lambda: baker.make_recipe('roleplay.world', owner=self.user)
        view.setup(self.rq)

        self.assertTrue(view.test_func())
