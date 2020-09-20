import json

from django.shortcuts import reverse
from django.test import RequestFactory, TestCase
from faker import Faker

from common.views import ResolverView


class TestResolverView(TestCase):
    view = ResolverView

    def setUp(self):
        self.faker = Faker()
        self.resolver = 'core:home'
        self.data_ok = {
            'url_resolver': self.resolver
        }
        self.url = reverse('common:utils:get_url')
        self.rq = RequestFactory().post(
            self.url,
            data=self.data_ok
        )

    def test_resolver_ok(self):
        response = self.view.as_view()(self.rq)
        data = json.loads(response.getvalue())

        self.assertEqual(reverse(self.resolver), data['url'])

    def test_resolver_ko(self):
        data_ko = self.data_ok.copy()
        data_ko['url_resolver'] = self.faker.word()
        rq = RequestFactory().post(self.url, data=data_ko)
        response = response = self.view.as_view()(rq)
        data = json.loads(response.getvalue())

        self.assertEqual('#no-url', data['url'])
