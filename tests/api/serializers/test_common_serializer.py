from django.apps import apps
from django.test import TestCase
from model_bakery import baker
from rest_framework import serializers

from api.serializers.common import MappedSerializerMixin
from api.serializers.registration import UserSerializer
from common.constants import models

Profile = apps.get_model(models.REGISTRATION_PROFILE)


class TestMappedSerializerMixin(TestCase):
    @classmethod
    def setUpTestData(cls):
        class DummyModelSerializer(MappedSerializerMixin, serializers.ModelSerializer):
            serializers_map = {
                'user': UserSerializer(many=False, read_only=True)
            }

            class Meta:
                model = Profile
                fields = ('id', 'user',)
        cls.user = baker.make_recipe('registration.user')
        cls.profile = cls.user.profile
        cls.model_serializer = DummyModelSerializer

    def test_normal_serialization_ok(self):
        data = self.model_serializer(instance=self.profile, many=False).data

        self.assertEqual(data['id'], self.profile.id)
        self.assertEqual(data['user'], self.user.pk)

    def test_mapped_serialization_ok(self):
        data = self.model_serializer(instance=self.profile, many=False, map_fields=['user']).data

        self.assertEqual(data['id'], self.profile.id)
        self.assertEqual(data['user']['id'], self.user.id)
        self.assertEqual(data['user']['username'], self.user.username)
