from django.apps import apps
from django.shortcuts import reverse
from faker import Faker
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APITestCase

from common.constants import models

fake = Faker()

Chat = apps.get_model(models.CHAT_MODEL)
ChatMessage = apps.get_model(models.CHAT_MESSAGE_MODEL)
User = apps.get_model(models.USER_MODEL)

base_resolver = 'api:chat'


class TestChatAPIRootViewSet(APITestCase):

    def test_anonymous_list_urls_ok(self):
        url = reverse(f'{base_resolver}:api-root')
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)


class TestChatViewSet(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.model = Chat

        cls.user = baker.make(User)
        cls.admin_user = baker.make(User, is_staff=True)

    def test_anonymous_list_ko(self):
        url = reverse(f'{base_resolver}:chat-list')
        response = self.client.get(url)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_authenticated_chat_list_ok(self):
        url = reverse(f'{base_resolver}:chat-list')
        self.client.force_login(self.user)
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_authenticated_chat_list_only_user_ok(self):
        """
        Checks if user can only see its own chat.
        """

        url = reverse(f'{base_resolver}:chat-list')
        self.client.force_login(self.user)

        # Creating data
        baker.make(_model=self.model, _quantity=fake.pyint(min_value=1, max_value=10))
        baker.make(_model=self.model, _quantity=fake.pyint(min_value=1, max_value=10), users=[self.user])
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        data = response.json()['results']
        expected_data = self.model.objects.filter(
            users__in=[self.user],
        ).count()

        self.assertEqual(expected_data, len(data))

    def test_authenticated_admin_chat_list_ok(self):
        """
        Checks if admin can list every chat.
        """

        url = reverse(f'{base_resolver}:chat-list')
        self.client.force_login(self.admin_user)

        # Creating data
        baker.make(_model=self.model, _quantity=fake.pyint(min_value=1, max_value=10))
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        data = response.json()['results']
        expected_data = self.model.objects.count()

        self.assertEqual(expected_data, len(data))

    def test_anonymous_detail_ko(self):
        chat = baker.make(self.model)
        url = reverse(f'{base_resolver}:chat-detail', kwargs={'pk': chat.pk})
        response = self.client.get(url)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_authenticated_user_not_in_chat_detail_ko(self):
        chat = baker.make(self.model)
        url = reverse(f'{base_resolver}:chat-detail', kwargs={'pk': chat.pk})
        self.client.force_login(self.user)
        response = self.client.get(url)

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_authenticated_user_in_chat_detail_ok(self):
        chat = baker.make(self.model, users=[self.user])
        baker.make(_model=self.model, _quantity=fake.pyint(min_value=1, max_value=10))
        url = reverse(f'{base_resolver}:chat-detail', kwargs={'pk': chat.pk})
        self.client.force_login(self.user)
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_authenticated_admin_chat_detail_ok(self):
        chat = baker.make(self.model)
        self.client.force_login(self.admin_user)
        url = reverse(f'{base_resolver}:chat-detail', kwargs={'pk': chat.pk})
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)


# noinspection DuplicatedCode
class TestChatMessageViewSet(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.model = ChatMessage

        cls.user = baker.make(User)
        cls.admin_user = baker.make(User, is_staff=True)
        cls.chat_with_user_in_it = baker.make(Chat, users=[cls.user])
        cls.chat_without_user_in_it = baker.make(Chat)

    def test_anonymous_message_list_ko(self):
        url = reverse(f'{base_resolver}:message-list')
        response = self.client.get(url)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_authenticated_not_admin_message_list_ok(self):
        baker.make(
            _model=self.model, _quantity=fake.pyint(min_value=1, max_value=10),
            message=fake.word(), author_id=self.user.pk,
        )
        baker.make(_model=self.model, _quantity=fake.pyint(min_value=1, max_value=10), message=fake.word())
        url = reverse(f'{base_resolver}:message-list')
        self.client.force_login(self.user)
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_data = self.model.objects.filter(
            author_id=self.user.id
        ).count()
        data = response.json()['results']

        self.assertEqual(expected_data, len(data))

    def test_authenticated_admin_message_list_ok(self):
        baker.make(_model=self.model, _quantity=fake.pyint(min_value=1, max_value=10), message=fake.word())
        url = reverse(f'{base_resolver}:message-list')
        self.client.force_login(self.admin_user)
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_data = self.model.objects.count()
        data = response.json()['results']

        self.assertEqual(expected_data, len(data))

    def test_authenticated_not_admin_user_in_chat_message_create_ok(self):
        self.client.force_login(self.user)
        url = reverse(f'{base_resolver}:message-list')
        data = {
            'chat': self.chat_with_user_in_it.pk,
            'message': fake.word(),
        }
        response = self.client.post(path=url, data=data)

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

    def test_authenticated_not_admin_user_not_in_chat_message_create_ko(self):
        self.client.force_login(self.user)
        url = reverse(f'{base_resolver}:message-list')
        data = {
            'chat': self.chat_without_user_in_it.pk,
            'message': fake.word(),
        }
        response = self.client.post(path=url, data=data)

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_authenticated_admin_user_in_chat_message_create_ok(self):
        self.client.force_login(self.admin_user)
        url = reverse(f'{base_resolver}:message-list')
        data = {
            'chat': self.chat_with_user_in_it.pk,
            'message': fake.word(),
            'author': self.user.pk,
        }
        response = self.client.post(path=url, data=data)

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

    def test_authenticated_admin_user_not_in_chat_message_create_ko(self):
        self.client.force_login(self.admin_user)
        url = reverse(f'{base_resolver}:message-list')
        data = {
            'chat': self.chat_without_user_in_it.pk,
            'message': fake.word(),
            'author': self.user.pk,
        }
        response = self.client.post(path=url, data=data)

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_anonymous_message_detail_ko(self):
        message = baker.make(self.model)
        url = reverse(f'{base_resolver}:message-detail', kwargs={'pk': message.pk})
        response = self.client.get(url)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_authenticated_not_admin_author_message_detail_ok(self):
        message = baker.make(self.model, author=self.user)
        self.client.force_login(self.user)
        url = reverse(f'{base_resolver}:message-detail', kwargs={'pk': message.pk})
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_authenticated_not_admin_not_author_message_detail_ko(self):
        message = baker.make(self.model)
        self.client.force_login(self.user)
        url = reverse(f'{base_resolver}:message-detail', kwargs={'pk': message.pk})
        response = self.client.get(url)

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_authenticated_admin_author_message_detail_ok(self):
        message = baker.make(self.model, author=self.admin_user)
        self.client.force_login(self.admin_user)
        url = reverse(f'{base_resolver}:message-detail', kwargs={'pk': message.pk})
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_authenticated_admin_not_author_message_detail_ok(self):
        message = baker.make(self.model, author=self.user)
        self.client.force_login(self.admin_user)
        url = reverse(f'{base_resolver}:message-detail', kwargs={'pk': message.pk})
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_authenticated_not_admin_author_message_partial_update_ok(self):
        message = baker.make(self.model, author=self.user)
        self.client.force_login(self.user)
        url = reverse(f'{base_resolver}:message-detail', kwargs={'pk': message.pk})
        data = {
            'message': fake.word(),
        }
        response = self.client.patch(path=url, data=data)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_authenticated_not_admin_not_author_message_partial_update_ko(self):
        message = baker.make(self.model)
        self.client.force_login(self.user)
        url = reverse(f'{base_resolver}:message-detail', kwargs={'pk': message.pk})
        data = {
            'message': fake.word(),
        }
        response = self.client.patch(path=url, data=data)

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_authenticated_admin_author_message_update_ok(self):
        message = baker.make(self.model, author=self.admin_user)
        self.client.force_login(self.admin_user)
        url = reverse(f'{base_resolver}:message-detail', kwargs={'pk': message.pk})
        data = {
            'message': fake.word(),
            'chat': message.chat.pk,
            'author': self.admin_user.pk,
        }
        response = self.client.put(path=url, data=data)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_authenticated_admin_not_author_message_update_ok(self):
        message = baker.make(self.model, author=self.user)
        self.client.force_login(self.admin_user)
        url = reverse(f'{base_resolver}:message-detail', kwargs={'pk': message.pk})
        data = {
            'message': fake.word(),
            'chat': message.chat.pk,
            'author': self.user.pk,
        }
        response = self.client.put(path=url, data=data)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_authenticated_not_admin_author_message_delete_ok(self):
        message = baker.make(self.model, author=self.user)
        self.client.force_login(self.user)
        url = reverse(f'{base_resolver}:message-detail', kwargs={'pk': message.pk})
        response = self.client.delete(url)

        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

    def test_authenticated_not_admin_not_author_message_delete_ko(self):
        message = baker.make(self.model)
        self.client.force_login(self.user)
        url = reverse(f'{base_resolver}:message-detail', kwargs={'pk': message.pk})
        response = self.client.delete(url)

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_authenticated_admin_author_message_delete_ok(self):
        message = baker.make(self.model, author=self.admin_user)
        self.client.force_login(self.admin_user)
        url = reverse(f'{base_resolver}:message-detail', kwargs={'pk': message.pk})
        response = self.client.delete(url)

        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

    def test_authenticated_admin_not_author_message_delete_ok(self):
        message = baker.make(self.model)
        self.client.force_login(self.admin_user)
        url = reverse(f'{base_resolver}:message-detail', kwargs={'pk': message.pk})
        response = self.client.delete(url)

        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
