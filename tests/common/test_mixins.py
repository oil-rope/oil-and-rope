import random

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse
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
        self.user = baker.make(get_user_model())
        self.url = '/{}/'.format(random.randint(1, 10))
        self.rq = RequestFactory().get(self.url)
        self.rq.method = 'GET'
        self.view = self.view()

    def test_dispatch_anonymous_user_ok(self):
        self.rq.user = AnonymousUser()
        self.view.setup(self.rq)
        response = self.view.dispatch(self.rq)
        self.assertIsInstance(response, HttpResponse)

    def test_dispatch_not_owner_attr(self):
        self.rq.user = self.user
        view = self.view
        view.owner_attr = None
        view.setup(self.rq)

        with self.assertRaises(ImproperlyConfigured) as ex:
            view.dispatch(self.rq)
        exception = ex.exception
        self.assertEqual(str(exception), 'OwnerRequiredMixin requires a definition of \'owner_attr\'.')
