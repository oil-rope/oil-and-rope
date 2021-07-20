from django.apps import apps
from django.test import TestCase
from faker import Faker
from model_bakery import baker

from api.serializers.registration import ProfileSerializer, UserSerializer
from common.constants import models

fake = Faker()

User = apps.get_model(models.USER_MODEL)
Profile = apps.get_model(models.PROFILE_MODEL)


class TestUserSerializer(TestCase):
    model = User
    serializer = UserSerializer

    def test_empty_data_ok(self):
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
