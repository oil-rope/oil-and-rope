from django.test import TestCase, RequestFactory

from common.context_processors.utils import requests_utils


class TestUtilsContextProcessor(TestCase):

    def setUp(self):
        self.request = RequestFactory()
        self.url = '/'
        self.get_request = RequestFactory().get(self.url)

    def test_requests_utils(self):
        ctx = requests_utils(self.get_request)
        host = 'testserver'
        port = '80'
        secure_uri = 'https://testserver'
        insecure_uri = 'http://testserver'
        real_uri = self.get_request.build_absolute_uri()

        self.assertEqual(ctx['host'], host)
        self.assertEqual(ctx['port'], port)
        self.assertEqual(ctx['secure_uri'], secure_uri)
        self.assertEqual(ctx['insecure_uri'], insecure_uri)
        self.assertEqual(ctx['real_uri'], real_uri)
