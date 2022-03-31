from django.apps import apps
from django.test import TestCase
from faker import Faker
from model_bakery import baker

from api.serializers.roleplay import DomainSerializer, PlaceSerializer, RaceSerializer, SessionSerializer
from common.constants import models
from roleplay.enums import SiteTypes

Domain = apps.get_model(models.DOMAIN_MODEL)
Place = apps.get_model(models.PLACE_MODEL)
Race = apps.get_model(models.RACE_MODEL)
Session = apps.get_model(models.SESSION_MODEL)
User = apps.get_model(models.USER_MODEL)

fake = Faker()


class TestDomainSerializer(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.model = Domain
        cls.serializer = DomainSerializer

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


class TestPlaceSerializer(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.model = Place
        cls.serializer = PlaceSerializer

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

    def test_serializer_with_children_ok(self):
        obj = baker.make_recipe('roleplay.place')
        children_obj = baker.make_recipe(
            'roleplay.place', _quantity=fake.pyint(min_value=1, max_value=10), parent_site=obj,
        )
        serialized_qs = self.serializer(obj)
        serialized_result = serialized_qs.data

        self.assertEqual(len(children_obj), len(serialized_result['children']))


class TestRaceSerializer(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.model = Race
        cls.serializer = RaceSerializer

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

    def test_serializer_users_is_list_ok(self):
        user = baker.make(User)
        obj = baker.make(self.model, users=[user])
        serialized_obj = self.serializer(obj)
        users = serialized_obj.data['users']

        self.assertIsInstance(users, list)
        self.assertListEqual([user.pk], users)

    def test_serializer_owners_is_list_ok(self):
        obj = baker.make(self.model)
        user = baker.make(User)
        obj.add_owners(user)
        serialized_obj = self.serializer(obj)
        owners = serialized_obj.data['owners']

        self.assertIsInstance(owners, list)
        self.assertListEqual([user.pk], owners)


class TestSessionSerializer(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.model = Session
        cls.serializer = SessionSerializer

        cls.world = baker.make(Place, site_type=SiteTypes.WORLD)

    def test_empty_data_ok(self):
        qs = self.model.objects.all()
        serialized_qs = self.serializer(qs, many=True)
        serialized_result = serialized_qs.data

        self.assertListEqual([], serialized_result)

    def test_serializer_with_data_ok(self):
        baker.make(_model=self.model, _quantity=fake.pyint(min_value=1, max_value=10), world=self.world)
        qs = self.model.objects.all()
        serialized_qs = self.serializer(qs, many=True)
        serialized_result = serialized_qs.data

        self.assertEqual(qs.count(), len(serialized_result))

    def test_serializer_object_ok(self):
        expected_name = fake.word()
        obj = baker.make(self.model, name=expected_name, world=self.world)
        serialized_qs = self.serializer(obj)
        serialized_result = serialized_qs.data

        self.assertEqual(expected_name, serialized_result['name'])
