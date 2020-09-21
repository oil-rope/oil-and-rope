from django.test import TestCase
from model_bakery import baker

from common.constants import models
from common.views import StaffRequiredMixin


class TestStaffRequiredMixin(TestCase):
    view = StaffRequiredMixin

    def setUp(self):
        self.user = baker.make(models.USER_MODEL)
        self.staff = baker.make(models.USER_MODEL, is_staff=True)

    def test_access_user_ko(self):
        self.client.force_login(self.user)
        rq = self.client.get('/').wsgi_request
        response = self.view.as_view()(rq)

        self.assertEqual(302, response.status_code)

    def test_access_staff_ok(self):
        self.client.force_login(self.staff)
        rq = self.client.get('/').wsgi_request
        self.view.as_view()(rq)
