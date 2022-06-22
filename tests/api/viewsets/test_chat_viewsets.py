from model_bakery import baker
from rest_framework.status import HTTP_200_OK, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND
from rest_framework.test import APITestCase

from chat.models import ChatMessage
from tests import fake


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

        self.assertNotIn(chat.pk, results)

    def test_retrieve_chat_where_user_is_not_member_ko(self):
        chat = baker.make_recipe('chat.chat')

        self.client.force_login(self.user)
        response = self.client.get(f'{self.url}{chat.pk}/')

        self.assertEqual(HTTP_404_NOT_FOUND, response.status_code)


class TestChatMessageViewSet(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = baker.make_recipe('registration.user')
        # Chat where user is member
        chat = baker.make_recipe('chat.chat')
        chat.users.add(cls.user)
        cls.message: ChatMessage = baker.make_recipe('chat.message', chat=chat, author=cls.user)

        cls.url = f'/api/chat/{chat.pk}/messages/'

    def test_anonymous_access_ko(self):
        response = self.client.get(self.url)

        self.assertEqual(HTTP_403_FORBIDDEN, response.status_code)

    def test_authenticated_access_ok(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(HTTP_200_OK, response.status_code)

    def test_create_ok(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url, data={'message': fake.sentence()}, format='json')
        message = response.json()
        message_instance: ChatMessage = ChatMessage.objects.get(pk=message['id'])

        self.assertEqual(message_instance.message, message['message'])

    def test_partial_update_ok(self):
        self.client.force_login(self.user)
        old_msg = self.message.message
        url = f'{self.url}{self.message.id}/'
        response = self.client.patch(url, data={'message': fake.sentence()}, format='json')
        message = response.json()

        self.assertNotEqual(old_msg, message['message'])
        self.message.refresh_from_db()
        self.assertEqual(self.message.message, message['message'])

    def test_partial_update_non_author_ko(self):
        msg: ChatMessage = baker.make_recipe('chat.message')

        url = f'{self.url}{msg.id}/'
        self.client.force_login(self.user)
        response = self.client.patch(url, data={'message': fake.sentence()}, format='json')

        self.assertEqual(HTTP_404_NOT_FOUND, response.status_code)
