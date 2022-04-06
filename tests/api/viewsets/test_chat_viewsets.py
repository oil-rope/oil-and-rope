from django.apps import apps
from django.contrib.auth import get_user_model
from django.shortcuts import resolve_url
from model_bakery import baker
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from api.serializers.registration import SimpleUserSerializer
from common.constants import models
from tests import fake

Chat = apps.get_model(models.CHAT_MODEL)
ChatMessage = apps.get_model(models.CHAT_MESSAGE_MODEL)
User = get_user_model()

base_resolver = 'api:chat'


class TestChatViewSet(APITestCase):
    model = Chat

    @classmethod
    def setUpTestData(cls):
        cls.user = baker.make_recipe('registration.user')
        cls.user_token = Token.objects.create(user=cls.user)
        cls.staff_user = baker.make_recipe('registration.staff_user')
        cls.staff_token = Token.objects.create(user=cls.staff_user)
        cls.user_credentials = {
            'HTTP_AUTHORIZATION': f'Token {cls.user_token.key}',
        }
        cls.staff_credentials = {
            'HTTP_AUTHORIZATION': f'Token {cls.staff_token.key}',
        }

    def test_anonymous_list_ko(self):
        url = resolve_url(f'{base_resolver}:chat-list')
        response = self.client.get(url)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_authenticated_list_ok(self):
        url = resolve_url(f'{base_resolver}:chat-list')
        self.client.credentials(**self.user_credentials)
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_authenticated_user_list_length_ok(self):
        """
        Checks if user can only see its own chat.
        """

        url = resolve_url(f'{base_resolver}:chat-list')
        self.client.credentials(**self.user_credentials)

        # Creating data
        baker.make_recipe(
            baker_recipe_name='chat.chat',
            _quantity=fake.pyint(min_value=1, max_value=10),
        )
        baker.make_recipe(
            baker_recipe_name='chat.chat',
            _quantity=fake.pyint(min_value=1, max_value=10),
            users=[self.user],
        )
        response = self.client.get(url)

        data = response.json()['results']
        expected_data = self.model.objects.filter(
            users__in=[self.user],
        ).count()

        self.assertEqual(expected_data, len(data))

    def test_authenticated_staff_list_ok(self):
        url = resolve_url(f'{base_resolver}:chat-list')
        self.client.credentials(**self.staff_credentials)
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_authenticated_staff_list_length_ok(self):
        """
        Checks if staff can only see its own chat.
        """

        url = resolve_url(f'{base_resolver}:chat-list')
        self.client.credentials(**self.staff_credentials)

        # Creating data
        baker.make_recipe(
            baker_recipe_name='chat.chat',
            _quantity=fake.pyint(min_value=1, max_value=10),
        )
        baker.make_recipe(
            baker_recipe_name='chat.chat',
            _quantity=fake.pyint(min_value=1, max_value=10),
            users=[self.staff_user],
        )
        response = self.client.get(url)

        data = response.json()['results']
        expected_data = self.model.objects.filter(
            users__in=[self.staff_user],
        ).count()

        self.assertEqual(expected_data, len(data))

    def test_authenticated_user_list_all_ko(self):
        url = resolve_url(f'{base_resolver}:chat-list-all')
        self.client.credentials(**self.user_credentials)
        response = self.client.get(url)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_authenticated_staff_list_all_ok(self):
        url = resolve_url(f'{base_resolver}:chat-list-all')
        self.client.credentials(**self.staff_credentials)
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_authenticated_staff_list_all_length_ok(self):
        chats = baker.make_recipe('chat.chat', _quantity=fake.pyint(min_value=1, max_value=10))
        url = resolve_url(f'{base_resolver}:chat-list-all')
        self.client.credentials(**self.staff_credentials)
        response = self.client.get(url)

        self.assertEqual(len(chats), len(response.json()['results']))

    def test_anonymous_detail_ko(self):
        chat = baker.make_recipe('chat.chat')
        url = resolve_url(f'{base_resolver}:chat-detail', pk=chat.pk)
        response = self.client.get(url)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_authenticated_user_not_in_chat_detail_ko(self):
        chat = baker.make_recipe('chat.chat')
        url = resolve_url(f'{base_resolver}:chat-detail', pk=chat.pk)
        self.client.credentials(**self.user_credentials)
        response = self.client.get(url)

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_authenticated_user_in_chat_detail_ok(self):
        chat = baker.make(self.model, users=[self.user])
        url = resolve_url(f'{base_resolver}:chat-detail', pk=chat.pk)
        self.client.credentials(**self.user_credentials)
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_authenticated_staff_detail_ok(self):
        chat = baker.make_recipe('chat.chat')
        self.client.force_login(self.staff_user)
        url = resolve_url(f'{base_resolver}:chat-detail', pk=chat.pk)
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_anonymous_nested_detail_ko(self):
        chat = baker.make_recipe('chat.chat')
        url = resolve_url(f'{base_resolver}:chat-detail-nested', pk=chat.pk)
        response = self.client.get(url)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_authenticated_user_not_in_chat_nested_detail_ko(self):
        chat = baker.make_recipe('chat.chat')
        url = resolve_url(f'{base_resolver}:chat-detail-nested', pk=chat.pk)
        self.client.credentials(**self.user_credentials)
        response = self.client.get(url)

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_authenticated_staff_chat_nested_detail_ok(self):
        chat = baker.make_recipe('chat.chat')
        url = resolve_url(f'{base_resolver}:chat-detail-nested', pk=chat.pk)
        self.client.credentials(**self.staff_credentials)
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)


class TestChatMessageViewSet(APITestCase):
    model = ChatMessage

    @classmethod
    def setUpTestData(cls):
        cls.user = baker.make_recipe('registration.user')
        cls.user_token = Token.objects.create(user=cls.user)
        cls.staff_user = baker.make_recipe('registration.staff_user')
        cls.staff_token = Token.objects.create(user=cls.staff_user)
        cls.chat_with_user_in_it = baker.make_recipe('chat.chat', users=[cls.user])
        cls.chat_without_user_in_it = baker.make_recipe('chat.chat')
        cls.user_credentials = {
            'HTTP_AUTHORIZATION': f'Token {cls.user_token.key}',
        }
        cls.staff_credentials = {
            'HTTP_AUTHORIZATION': f'Token {cls.staff_token.key}',
        }

    def test_anonymous_list_ko(self):
        url = resolve_url(f'{base_resolver}:message-list')
        response = self.client.get(url)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_authenticated_user_list_ok(self):
        url = resolve_url(f'{base_resolver}:message-list')
        self.client.credentials(**self.user_credentials)
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_authenticated_user_list_length_ok(self):
        messages = baker.make_recipe(
            baker_recipe_name='chat.message',
            _quantity=fake.pyint(min_value=1, max_value=10),
            author=self.user,
        )
        baker.make_recipe('chat.message', _quantity=fake.pyint(min_value=1, max_value=10))
        url = resolve_url(f'{base_resolver}:message-list')
        self.client.credentials(**self.user_credentials)
        response = self.client.get(url)

        self.assertEqual(len(messages), len(response.json()['results']))

    def test_authenticated_staff_list_ok(self):
        url = resolve_url(f'{base_resolver}:message-list')
        self.client.credentials(**self.staff_credentials)
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_authenticated_staff_list_length_ok(self):
        """
        Checks if staff can only see their own messages.
        """

        url = resolve_url(f'{base_resolver}:message-list')
        self.client.credentials(**self.staff_credentials)

        # Creating data
        baker.make_recipe(
            baker_recipe_name='chat.message',
            _quantity=fake.pyint(min_value=1, max_value=10),
        )
        baker.make_recipe(
            baker_recipe_name='chat.message',
            _quantity=fake.pyint(min_value=1, max_value=10),
            author=self.staff_user,
        )
        response = self.client.get(url)

        data = response.json()['results']
        expected_data = self.model.objects.filter(
            author__in=[self.staff_user],
        ).count()

        self.assertEqual(expected_data, len(data))

    def test_authenticated_user_list_all_ko(self):
        url = resolve_url(f'{base_resolver}:message-list-all')
        self.client.credentials(**self.user_credentials)
        response = self.client.get(url)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_authenticated_staff_list_all_ok(self):
        url = resolve_url(f'{base_resolver}:message-list-all')
        self.client.credentials(**self.staff_credentials)
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_authenticated_user_create_with_correct_data_ok(self):
        url = resolve_url(f'{base_resolver}:message-list')
        self.client.credentials(**self.user_credentials)
        data = {
            'chat': self.chat_with_user_in_it.pk,
            'message': fake.sentence(),
        }
        response = self.client.post(url, data=data, format='json')

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

    def test_authenticated_user_create_with_other_author_id_ko(self):
        user = baker.make('registration.user')
        url = resolve_url(f'{base_resolver}:message-list')
        self.client.credentials(**self.user_credentials)
        data = {
            'chat': self.chat_with_user_in_it.pk,
            'message': fake.sentence(),
            'author': user.pk,
        }
        response = self.client.post(url, data=data, format='json')

        self.assertEqual(self.user.pk, response.json()['author'])

    def test_authenticated_user_create_with_other_author_json_ko(self):
        user = baker.make('registration.user')
        user = SimpleUserSerializer(user).data
        url = resolve_url(f'{base_resolver}:message-list')
        self.client.credentials(**self.user_credentials)
        data = {
            'chat': self.chat_with_user_in_it.pk,
            'message': fake.sentence(),
            'author': user,
        }
        response = self.client.post(url, data=data, format='json')

        # Directly not correct format
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_authenticated_staff_create_with_other_author_id_ok(self):
        another_user = baker.make('registration.user')
        url = resolve_url(f'{base_resolver}:message-list')
        self.client.credentials(**self.staff_credentials)
        data = {
            'chat': self.chat_with_user_in_it.pk,
            'message': fake.sentence(),
            'author': another_user.pk,
        }
        response = self.client.post(url, data=data, format='json')

        # Directly not correct format
        self.assertEqual(another_user.pk, response.json()['author'])

    def test_authenticated_user_author_message_partial_update_correct_data_ok(self):
        message = baker.make_recipe('chat.message', author=self.user)
        self.client.credentials(**self.user_credentials)
        url = resolve_url(f'{base_resolver}:message-detail', pk=message.pk)
        data = {
            'message': fake.word(),
        }
        response = self.client.patch(path=url, data=data, format='json')

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_authenticated_user_author_partial_update_changes_chat_ko(self):
        message = baker.make_recipe('chat.message', author=self.user)
        another_chat = baker.make_recipe('chat.chat')
        self.client.credentials(**self.user_credentials)
        url = resolve_url(f'{base_resolver}:message-detail', pk=message.pk)
        data = {
            'message': fake.word(),
            'chat': another_chat.pk,
        }
        response = self.client.patch(path=url, data=data, format='json')

        self.assertEqual(message.chat.pk, response.json()['chat'])

    def test_authenticated_user_not_author_message_partial_update_ko(self):
        message = baker.make_recipe('chat.message')
        self.client.credentials(**self.user_credentials)
        url = resolve_url(f'{base_resolver}:message-detail', pk=message.pk)
        data = {
            'message': fake.word(),
        }
        response = self.client.patch(path=url, data=data, format='json')

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_authenticated_user_updates_message_ko(self):
        author = self.user
        message = baker.make_recipe('chat.message', author=author)
        self.client.credentials(**self.user_credentials)
        url = resolve_url(f'{base_resolver}:message-detail', pk=message.pk)
        data = {
            'message': fake.word(),
            'chat': message.chat.pk,
            'author': author.pk,
        }
        response = self.client.put(path=url, data=data, format='json')

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_authenticated_staff_message_update_with_same_author_ok(self):
        author = baker.make_recipe('registration.user')
        message = baker.make_recipe('chat.message', author=author)
        self.client.credentials(**self.staff_credentials)
        url = resolve_url(f'{base_resolver}:message-detail', pk=message.pk)
        data = {
            'message': fake.word(),
            'chat': message.chat.pk,
            'author': author.pk,
        }
        response = self.client.put(path=url, data=data, format='json')

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_authenticated_staff_message_update_with_same_author_updates_message_ok(self):
        author = baker.make_recipe('registration.user')
        message = baker.make_recipe('chat.message', author=author)
        self.client.credentials(**self.staff_credentials)
        url = resolve_url(f'{base_resolver}:message-detail', pk=message.pk)
        data = {
            'message': fake.word(),
            'chat': message.chat.pk,
            'author': author.pk,
        }
        response = self.client.put(path=url, data=data, format='json')

        self.assertNotEqual(message.message, response.json()['message'])

    def test_authenticated_staff_message_update_with_different_author_ok(self):
        author = baker.make_recipe('registration.user')
        diff_author = baker.make_recipe('registration.user')
        message = baker.make_recipe('chat.message', author=author)
        self.client.credentials(**self.staff_credentials)
        url = resolve_url(f'{base_resolver}:message-detail', pk=message.pk)
        data = {
            'message': fake.word(),
            'chat': message.chat.pk,
            'author': diff_author.pk,
        }
        response = self.client.put(path=url, data=data, format='json')

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_authenticated_staff_message_update_with_different_author_updates_author_ok(self):
        author = baker.make_recipe('registration.user')
        diff_author = baker.make_recipe('registration.user')
        message = baker.make_recipe('chat.message', author=author)
        self.client.credentials(**self.staff_credentials)
        url = resolve_url(f'{base_resolver}:message-detail', pk=message.pk)
        data = {
            'message': fake.word(),
            'chat': message.chat.pk,
            'author': diff_author.pk,
        }
        response = self.client.put(path=url, data=data, format='json')

        self.assertEqual(diff_author.pk, response.json()['author'])

    def test_authenticated_user_author_message_delete_ok(self):
        message = baker.make_recipe('chat.message', author=self.user)
        self.client.credentials(**self.user_credentials)
        url = resolve_url(f'{base_resolver}:message-detail', pk=message.pk)
        response = self.client.delete(url)

        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

    def test_authenticated_user_not_author_message_delete_ko(self):
        message = baker.make_recipe('chat.message')
        self.client.credentials(**self.user_credentials)
        url = resolve_url(f'{base_resolver}:message-detail', pk=message.pk)
        response = self.client.delete(url)

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_authenticated_staff_message_delete_ok(self):
        message = baker.make_recipe('chat.message')
        self.client.credentials(**self.staff_credentials)
        url = resolve_url(f'{base_resolver}:message-detail', pk=message.pk)
        response = self.client.delete(url)

        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
