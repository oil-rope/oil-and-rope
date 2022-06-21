import unittest

from django.apps import apps
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from model_bakery import baker

from api.serializers.roleplay import CampaignSerializer, DomainSerializer, PlaceSerializer, RaceSerializer
from common.constants import models
from roleplay.models import Campaign
from tests import fake
from tests.bot.helpers.constants import CHANNEL, LITECORD_API_URL, LITECORD_TOKEN
from tests.utils import check_litecord_connection

Domain = apps.get_model(models.ROLEPLAY_DOMAIN)
Place = apps.get_model(models.ROLEPLAY_PLACE)
Race = apps.get_model(models.ROLEPLAY_RACE)
Session = apps.get_model(models.ROLEPLAY_SESSION)
User = get_user_model()


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


class TestCampaignSerializer(TestCase):
    serializer_class = CampaignSerializer

    @classmethod
    def setUpTestData(cls):
        cls.instance: Campaign = baker.make_recipe('roleplay.campaign')

    def test_get_discord_channel_with_empty_discord_channel_id_ok(self):
        serializer = self.serializer_class(self.instance)

        self.assertIsNone(serializer.data['discord_channel'])

    @unittest.skipIf(not check_litecord_connection(), 'Litecord seems to be unreachable.')
    @override_settings(DISCORD_API_URL=LITECORD_API_URL, BOT_TOKEN=LITECORD_TOKEN)
    def test_get_discord_channel_with_discord_channel_id_ok(self):
        self.instance.discord_channel_id = CHANNEL
        serializer = self.serializer_class(self.instance)

        self.assertIsNotNone(serializer.data['discord_channel'])
