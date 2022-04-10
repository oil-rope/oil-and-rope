from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from model_bakery import baker

from api.serializers.registration import BotSerializer, ProfileSerializer, UserSerializer
from common.constants import models
from tests import fake

User = get_user_model()
Profile = apps.get_model(models.PROFILE_MODEL)


class TestUserSerializer(TestCase):
    model = User
    serializer = UserSerializer

    def test_serializer_with_data_ok(self):
        baker.make(_model=self.model, _quantity=fake.pyint(min_value=1, max_value=10))
        queryset = self.model.objects.all()
        serialized_qs = self.serializer(queryset, many=True)
        serialized_result = serialized_qs.data

        self.assertEqual(queryset.count(), len(serialized_result))

    def test_serializer_with_object_ok(self):
        expected_username = fake.user_name()
        obj = baker.make(self.model, username=expected_username)
        serialized_obj = self.serializer(obj)
        serialized_result = serialized_obj.data

        self.assertEqual(expected_username, serialized_result['username'])


class TestProfileSerializer(TestCase):
    model = Profile
    serializer = ProfileSerializer

    def test_empty_data_ok(self):
        queryset = self.model.objects.all()
        serialized_qs = self.serializer(queryset, many=True)
        serialized_result = serialized_qs.data

        self.assertListEqual([], serialized_result)

    def test_serializer_with_data_ok(self):
        # Since user and profile creates at once with only need User instances
        baker.make(_model=User, _quantity=fake.pyint(min_value=1, max_value=10))
        queryset = self.model.objects.all()
        serialized_qs = self.serializer(queryset, many=True)
        serialized_result = serialized_qs.data

        self.assertEqual(queryset.count(), len(serialized_result))

    def test_serializer_with_object_ok(self):
        expected_bio = fake.paragraph()
        user = baker.make(User)
        obj = user.profile
        obj.bio = expected_bio
        obj.save(update_fields=['bio'])
        serialized_obj = self.serializer(obj)
        serialized_result = serialized_obj.data

        self.assertEqual(expected_bio, serialized_result['bio'])


class TestBotSerializer(TestCase):
    serializer_class = BotSerializer

    @classmethod
    def setUpTestData(cls):
        cls.bot = User.objects.get(email=settings.DEFAULT_FROM_EMAIL)

    def test_command_prefix_ok(self):
        serialized_obj = self.serializer_class(self.bot)
        serialized_result = serialized_obj.data

        self.assertEqual(settings.BOT_COMMAND_PREFIX, serialized_result['command_prefix'])

    def test_description_ok(self):
        serialized_obj = self.serializer_class(self.bot)
        serialized_result = serialized_obj.data

        self.assertEqual(settings.BOT_DESCRIPTION, serialized_result['description'])
