from model_bakery import baker
from rest_framework.status import HTTP_200_OK, HTTP_403_FORBIDDEN
from rest_framework.test import APITestCase


class TestChatViewSet(APITestCase):
    url = '/api/chat/'

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = baker.make_recipe('registration.user')
        # Chat where user is member
        cls.chat = baker.make_recipe('chat.chat')
        cls.chat.users.add(cls.user)

    def test_anonymous_access_ko(self):
        response = self.client.get(self.url)

        self.assertEqual(HTTP_403_FORBIDDEN, response.status_code)

    def test_authenticated_access_ok(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(HTTP_200_OK, response.status_code)

    def test_user_cannot_see_chat_where_is_not_member_ok(self):
        chat = baker.make_recipe('chat.chat')
        chat.users.add(baker.make_recipe('registration.user'))

        self.client.force_login(self.user)
        response = self.client.get(self.url)
        results = [r['id'] for r in response.json()['results']]

        self.assertNotIn(chat.id, results)


class TestChatMessageViewSet(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = baker.make_recipe('registration.user')
        # Chat where user is member
        chat = baker.make_recipe('chat.chat')
        chat.users.add(cls.user)
        baker.make_recipe('chat.message', chat=chat)

        cls.url = f'/api/chat/{chat.id}/messages/'

    def test_anonymous_access_ko(self):
        response = self.client.get(self.url)

        self.assertEqual(HTTP_403_FORBIDDEN, response.status_code)

    def test_authenticated_access_ok(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(HTTP_200_OK, response.status_code)
