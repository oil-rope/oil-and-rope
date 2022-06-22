from model_bakery import baker
from rest_framework.status import HTTP_200_OK, HTTP_403_FORBIDDEN
from rest_framework.test import APITestCase


class TestUserViewSet(APITestCase):
    url = '/api/registration/user/'

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = baker.make_recipe('registration.user')

    def test_access_anonymous_ko(self):
        response = self.client.get(self.url)

        self.assertEqual(HTTP_403_FORBIDDEN, response.status_code)

    def test_access_logged_ok(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(HTTP_200_OK, response.status_code)


class TestBotViewSet(APITestCase):
    url = '/api/registration/bot/'

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = baker.make_recipe('registration.user')

    def test_access_anonymous_ko(self):
        response = self.client.get(self.url)

        self.assertEqual(HTTP_403_FORBIDDEN, response.status_code)

    def test_access_logged_ok(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(HTTP_200_OK, response.status_code)
