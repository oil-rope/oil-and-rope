from django.apps import apps
from django.test import TestCase
from faker import Faker
from model_bakery import baker

from api.serializers.dynamic_menu import DynamicMenuSerializer
from common.constants import models

DynamicMenu = apps.get_model(models.DYNAMIC_MENU)

fake = Faker()


class TestDynamicMenuSerializer(TestCase):
    model = DynamicMenu
    serializer = DynamicMenuSerializer

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
        expected_name = fake.word()
        obj = baker.make(self.model, name=expected_name)
        serialized_obj = self.serializer(obj)
        serialized_result = serialized_obj.data

        self.assertEqual(expected_name, serialized_result['name'])
