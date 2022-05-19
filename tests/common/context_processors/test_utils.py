from django.test import RequestFactory, TestCase

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
        uri = 'http://testserver'
        current_uri = self.get_request.build_absolute_uri()

        self.assertEqual(ctx['host'], host)
        self.assertEqual(ctx['port'], port)
        self.assertEqual(ctx['uri'], uri)
        self.assertEqual(ctx['current_uri'], current_uri)
