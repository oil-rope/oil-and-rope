from django.apps import apps
from django.test import TestCase
from faker import Faker
from model_bakery import baker

from api.serializers.roleplay import DomainSerializer
from common.constants import models

Domain = apps.get_model(models.DOMAIN_MODEL)

fake = Faker()


class TestDomainSerializer(TestCase):
    model = Domain
    serializer = DomainSerializer

    def test_empty_data_ok(self):
        qs = self.model.objects.all()
        serialized_qs = self.serializer(qs, many=True)
        serialized_result = serialized_qs.data

        self.assertListEqual([], serialized_result)

    def test_serializer_with_data_ok(self):
        baker.make(_model=self.model, _quantity=fake.pyint(min_value=1, max_value=10))
        qs = self.model.objects.all()
        serialized_qs = self.serializer(qs, many=True)
        serialized_result = serialized_qs.data

        self.assertEqual(qs.count(), len(serialized_result))

    def test_serializer_object_ok(self):
        expected_name = fake.word()
        obj = baker.make(self.model, name=expected_name)
        serialized_qs = self.serializer(obj)
        serialized_result = serialized_qs.data

        self.assertEqual(expected_name, serialized_result['name'])
