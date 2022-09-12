from django.apps import apps
from django.test import TestCase
from model_bakery import baker

from api.serializers.chat import (ChatMessageSerializer, ChatSerializer, NestedChatMessageSerializer,
                                  NestedChatSerializer)
from common.constants import models
from tests.utils import fake

Chat = apps.get_model(models.CHAT)
ChatMessage = apps.get_model(models.CHAT_MESSAGE)


class TestChatMessageSerializer(TestCase):
    model = ChatMessage
    serializer_class = ChatMessageSerializer

    @classmethod
    def setUpTestData(cls):
        cls.message = baker.make_recipe('chat.message')

    def test_id_is_int_ok(self):
        serialized_obj = self.serializer_class(self.message)
        serialized_data = serialized_obj.data

        self.assertTrue(isinstance(serialized_data['id'], int))

    def test_chat_is_int_ok(self):
        serialized_obj = self.serializer_class(self.message)
        serialized_data = serialized_obj.data

        self.assertTrue(isinstance(serialized_data['chat'], int))

    def test_message_is_str_ok(self):
        serialized_obj = self.serializer_class(self.message)
        serialized_data = serialized_obj.data

        self.assertTrue(isinstance(serialized_data['message'], str))

    def test_author_is_int_ok(self):
        serialized_obj = self.serializer_class(self.message)
        serialized_data = serialized_obj.data

        self.assertTrue(isinstance(serialized_data['author'], int))

    def test_entry_created_at_is_str_ok(self):
        serialized_obj = self.serializer_class(self.message)
        serialized_data = serialized_obj.data

        self.assertTrue(isinstance(serialized_data['entry_created_at'], str))

    def test_entry_updated_at_is_str_ok(self):
        serialized_obj = self.serializer_class(self.message)
        serialized_data = serialized_obj.data

        self.assertTrue(isinstance(serialized_data['entry_updated_at'], str))


class TestNestedChatMessageSerializer(TestCase):
    model = ChatMessage
    serializer_class = NestedChatMessageSerializer

    @classmethod
    def setUpTestData(cls):
        cls.message = baker.make_recipe('chat.message')

    def test_id_is_int_ok(self):
        serialized_obj = self.serializer_class(self.message)
        serialized_data = serialized_obj.data

        self.assertTrue(isinstance(serialized_data['id'], int))

    def test_chat_is_int_ok(self):
        serialized_obj = self.serializer_class(self.message)
        serialized_data = serialized_obj.data

        self.assertTrue(isinstance(serialized_data['chat'], int))

    def test_message_is_str_ok(self):
        serialized_obj = self.serializer_class(self.message)
        serialized_data = serialized_obj.data

        self.assertTrue(isinstance(serialized_data['message'], str))

    def test_author_is_dict_ok(self):
        serialized_obj = self.serializer_class(self.message)
        serialized_data = serialized_obj.data

        self.assertTrue(isinstance(serialized_data['author'], dict))

    def test_entry_created_at_is_str_ok(self):
        serialized_obj = self.serializer_class(self.message)
        serialized_data = serialized_obj.data

        self.assertTrue(isinstance(serialized_data['entry_created_at'], str))

    def test_entry_updated_at_is_str_ok(self):
        serialized_obj = self.serializer_class(self.message)
        serialized_data = serialized_obj.data

        self.assertTrue(isinstance(serialized_data['entry_updated_at'], str))


class TestChatSerializer(TestCase):
    model = Chat
    serializer_class = ChatSerializer

    @classmethod
    def setUpTestData(cls):
        users = baker.make_recipe('registration.user', _quantity=fake.pyint(min_value=1, max_value=10))
        messages = baker.make_recipe('chat.message', _quantity=fake.pyint(min_value=1, max_value=10))
        cls.chat = baker.make_recipe(
            baker_recipe_name='chat.chat',
            users=users,
            chat_message_set=messages,
        )

    def test_id_is_int_ok(self):
        serialized_obj = self.serializer_class(self.chat)
        serialized_data = serialized_obj.data

        self.assertTrue(isinstance(serialized_data['id'], int))

    def test_name_is_str_ok(self):
        serialized_obj = self.serializer_class(self.chat)
        serialized_data = serialized_obj.data

        self.assertTrue(isinstance(serialized_data['name'], str))

    def test_users_is_list_ok(self):
        serialized_obj = self.serializer_class(self.chat)
        serialized_data = serialized_obj.data

        self.assertTrue(isinstance(serialized_data['users'], list))

    def test_chat_message_set_is_list_ok(self):
        serialized_obj = self.serializer_class(self.chat)
        serialized_data = serialized_obj.data

        self.assertTrue(isinstance(serialized_data['chat_message_set'], list))

    def test_entry_created_at_is_str_ok(self):
        serialized_obj = self.serializer_class(self.chat)
        serialized_data = serialized_obj.data

        self.assertTrue(isinstance(serialized_data['entry_created_at'], str))

    def test_entry_updated_at_is_str_ok(self):
        serialized_obj = self.serializer_class(self.chat)
        serialized_data = serialized_obj.data

        self.assertTrue(isinstance(serialized_data['entry_updated_at'], str))


class TestNestedChatSerializer(TestCase):
    model = apps.get_model(models.CHAT)
    serializer_class = NestedChatSerializer

    @classmethod
    def setUpTestData(cls):
        cls.user_set = baker.make_recipe('registration.user', _quantity=fake.pyint(min_value=1, max_value=10))
        cls.chat_without_messages = baker.make_recipe('chat.chat', users=cls.user_set)
        cls.chat_with_messages = baker.make_recipe('chat.chat', users=cls.user_set)
        baker.make_recipe(
            'chat.message',
            _quantity=fake.pyint(min_value=1, max_value=10),
            chat=cls.chat_with_messages,
        )

    def test_id_is_int_ok(self):
        serialized_obj = self.serializer_class(self.chat_without_messages)
        serialized_data = serialized_obj.data

        self.assertTrue(isinstance(serialized_data['id'], int))

    def test_name_is_str_ok(self):
        serialized_obj = self.serializer_class(self.chat_without_messages)
        serialized_data = serialized_obj.data

        self.assertTrue(isinstance(serialized_data['name'], str))

    def test_users_is_list_ok(self):
        serialized_obj = self.serializer_class(self.chat_without_messages)
        serialized_data = serialized_obj.data

        self.assertTrue(isinstance(serialized_data['users'], list))

    def test_chat_message_set_is_list_ok(self):
        serialized_obj = self.serializer_class(self.chat_without_messages)
        serialized_data = serialized_obj.data

        self.assertTrue(isinstance(serialized_data['chat_message_set'], list))

    def test_entry_created_at_is_str_ok(self):
        serialized_obj = self.serializer_class(self.chat_without_messages)
        serialized_data = serialized_obj.data

        self.assertTrue(isinstance(serialized_data['entry_created_at'], str))

    def test_entry_updated_at_is_str_ok(self):
        serialized_obj = self.serializer_class(self.chat_without_messages)
        serialized_data = serialized_obj.data

        self.assertTrue(isinstance(serialized_data['entry_updated_at'], str))

    def test_nested_chat_message_set_is_dict(self):
        serialized_obj = self.serializer_class(self.chat_with_messages)
        serialized_data = serialized_obj.data

        self.assertTrue(isinstance(serialized_data['chat_message_set'][0], dict))
