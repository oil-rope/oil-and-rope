import json

from django.apps import apps
from django.conf import settings
from django.shortcuts import resolve_url
from django.test import RequestFactory, TestCase
from model_bakery import baker

from common.constants import models as constants
from common.views import json as views
from tests import fake

Vote = apps.get_model(constants.COMMON_VOTE)


class TestResolverView(TestCase):
    to_resolve = 'common:utils:get_url'
    view = views.ResolverView

    def setUp(self):
        self.url = resolve_url(self.to_resolve)
        self.to_resolve = 'core:home'
        self.data_ok = {
            'url_resolver': self.to_resolve
        }
        self.rq = RequestFactory().post(
            self.url,
            data=self.data_ok
        )

    def test_resolver_ok(self):
        response = self.view.as_view()(self.rq)
        data = json.loads(response.getvalue())

        self.assertEqual(resolve_url(self.to_resolve), data['url'])

    def test_resolver_ko(self):
        data_ko = self.data_ok.copy()
        data_ko['url_resolver'] = fake.word()
        rq = RequestFactory().post(self.url, data=data_ko)
        response = response = self.view.as_view()(rq)
        data = json.loads(response.getvalue())

        self.assertEqual('#no-url', data['url'])


class TestVoteView(TestCase):
    login_url = resolve_url(settings.LOGIN_URL)
    resolver = 'common:utils:vote'
    view = views.VoteView

    @classmethod
    def setUpTestData(cls):
        cls.user = baker.make_recipe('registration.user')
        cls.instance = baker.make_recipe('roleplay.campaign')
        cls.model = f'{cls.instance._meta.app_label}.{cls.instance._meta.model_name}'
        cls.pk = cls.instance.pk

    def setUp(self):
        self.url = resolve_url(self.resolver, model=self.model, pk=self.pk)
        self.rq = RequestFactory().get(self.url)

    def test_access_anonymous_ko(self):
        response = self.client.get(self.url)
        expected_url = f'{self.login_url}?next={self.url}'

        self.assertRedirects(response, expected_url)

    def test_access_authenticated_ok(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(200, response.status_code)

    def test_access_authenticated_non_existent_model_ko(self):
        self.client.force_login(self.user)
        url = resolve_url(self.resolver, model='fake_label.fake_model', pk=self.pk)
        response = self.client.get(url)

        self.assertEqual(404, response.status_code)

    def test_access_authenticated_non_existent_pk_ko(self):
        self.client.force_login(self.user)
        url = resolve_url(self.resolver, model=self.model, pk=fake.pyint())
        response = self.client.get(url)

        self.assertEqual(404, response.status_code)

    def test_access_authenticated_update_vote_ok(self):
        self.client.force_login(self.user)
        baker.make(Vote, user=self.user, is_positive=False)
        response = self.client.get(self.url, is_positive=True)
        vote = Vote.objects.get(pk=response.json()['id'])

        self.assertTrue(vote.is_positive)
