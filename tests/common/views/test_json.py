import json

from django.shortcuts import reverse
from django.test import RequestFactory, TestCase

from common.views import ResolverView


class TestResolverView(TestCase):
    view = ResolverView

    def setUp(self):
        self.resolver = 'core:home'
        self.data_ok = {
            'url_resolver': self.resolver
        }
        self.url = reverse('common:utils:get_url')
        self.rq = RequestFactory().post(
            self.url,
            data=self.data_ok
        )

    def test_post_ok(self):
        response = self.view.as_view()(self.rq)
        data = json.loads(response.getvalue())

        self.assertTrue(reverse(self.resolver), data['url'])
