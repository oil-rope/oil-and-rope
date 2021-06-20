from itertools import cycle

from django.apps import apps
from django.test import TestCase
from faker import Faker
from model_bakery import baker

from api.serializers.chat import ChatMessageSerializer, ChatSerializer
from common.constants import models

fake = Faker()


class TestChatMessageSerializer(TestCase):
    model = apps.get_model(models.CHAT_MESSAGE_MODEL)
    serializer = ChatMessageSerializer

    def test_empty_serializer_ok(self):
        queryset = self.model.objects.all()
        serialized_qs = self.serializer(queryset, many=True)
        serialized_result = serialized_qs.data

        self.assertListEqual([], serialized_result)

    def test_serializer_with_data_ok(self):
        baker.make(_model=self.model, _quantity=fake.pyint(min_value=1, max_value=10))
        queryset = self.model.objects.all()
        serialized_qs = self.serializer(queryset, many=True)
        serialized_result = serialized_qs.data

        self.assertEqual(queryset.count(), len(serialized_result))

    def test_serializer_with_object_ok(self):
        expected_message = fake.word()
        obj = baker.make(self.model, message=expected_message)
        serialized_obj = self.serializer(obj)
        serialized_result = serialized_obj.data

        self.assertEqual(expected_message, serialized_result['message'])


class TestChatSerializer(TestCase):
    model = apps.get_model(models.CHAT_MODEL)
    serializer = ChatSerializer

    def test_serializer_empty_ok(self):
        queryset = self.model.objects.all()
        serialized_qs = self.serializer(queryset, many=True)
        serialized_result = serialized_qs.data

        self.assertListEqual([], serialized_result)

    def test_serializer_with_data_ok(self):
        baker.make(_model=self.model, _quantity=fake.pyint(min_value=1, max_value=10))
        queryset = self.model.objects.all()
        serialized_qs = self.serializer(queryset, many=True)
        serialized_result = serialized_qs.data

        self.assertEqual(queryset.count(), len(serialized_result))

    def test_serializer_with_object_ok(self):
        expected_name = fake.word()
        obj = baker.make(self.model, name=expected_name)
        serialized_obj = self.serializer(obj)
        serialized_result = serialized_obj.data

        self.assertEqual(expected_name, serialized_result['name'])

    def test_serializer_with_users_ok(self):
        users = baker.make(_model=models.USER_MODEL, _quantity=fake.pyint(min_value=1, max_value=10))
        obj = baker.make(_model=self.model, users=users)
        serialized_obj = self.serializer(obj)
        serialized_result = serialized_obj.data

        self.assertListEqual([user.id for user in users], serialized_result['users'])

    def test_serializer_with_messages_ok(self):
        iterations = fake.pyint(min_value=1, max_value=6)
        expected_messages = [fake.word() for _ in range(0, iterations)]
        obj = baker.make(self.model)
        baker.make(_model=models.CHAT_MESSAGE_MODEL, _quantity=iterations, message=cycle(expected_messages), chat=obj)
        serialized_obj = self.serializer(obj)
        serialized_result = serialized_obj.data

        messages = [m['message'] for m in serialized_result['chat_message_set']]
        self.assertListEqual(expected_messages, messages)
