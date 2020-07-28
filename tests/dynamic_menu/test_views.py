from unittest import mock

from django.shortcuts import reverse
from django.test import TestCase
from model_bakery import baker

from common.constants import models as constants
from dynamic_menu import views


class TestDynamicMenuCreateView(TestCase):
    view = views.DynamicMenuCreateView

    def setUp(self):
        self.user = baker.make(constants.USER_MODEL)
        self.staff_user = baker.make(constants.USER_MODEL, is_staff=True)
        self.url = reverse('dynamic_menu:dynamic_menu:create')

    def test_access_anonymous_user_ko(self):
        response = self.client.get(self.url)

        self.assertEqual(302, response.status_code)

    @mock.patch('common.views.auth.messages')
    def test_access_non_staff_user_ko(self, mock_call):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(302, response.status_code)
        warn_message = 'You are trying to access an Staff page but you are not staff.'

        mock_call.warning.assert_called_with(
            response.wsgi_request,
            warn_message
        )

    def test_acess_staff_user_ok(self):
        self.client.force_login(self.staff_user)
        response = self.client.get(self.url)

        self.assertEqual(200, response.status_code)
