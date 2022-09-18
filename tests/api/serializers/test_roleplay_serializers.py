from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

from django.apps import apps
from django.contrib.auth import get_user_model
from django.test import TestCase
from model_bakery import baker

from api.serializers.roleplay import CampaignSerializer, DomainSerializer, PlaceNestedSerializer, RaceSerializer
from common.constants import models
from tests.mocks import discord
from tests.utils import fake

if TYPE_CHECKING:
    from registration.models import User as UserModel
    from roleplay.models import Campaign as CampaignModel
    from roleplay.models import Domain as DomainModel
    from roleplay.models import Place as PlaceModel
    from roleplay.models import Race as RaceModel
    from roleplay.models import Session as SessionModel

Domain: 'DomainModel' = apps.get_model(models.ROLEPLAY_DOMAIN)
Place: 'PlaceModel' = apps.get_model(models.ROLEPLAY_PLACE)
Race: 'RaceModel' = apps.get_model(models.ROLEPLAY_RACE)
Session: 'SessionModel' = apps.get_model(models.ROLEPLAY_SESSION)
User: 'UserModel' = get_user_model()


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
        cls.serializer = PlaceNestedSerializer

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

    def setUp(self):
        self.instance: 'CampaignModel' = baker.make_recipe('roleplay.campaign')

    def test_get_discord_channel_with_empty_discord_channel_id_ok(self):
        serializer = self.serializer_class(self.instance)

        self.assertIsNone(serializer.data['discord_channel'])

    @patch('bot.utils.discord_api_request')
    def test_get_discord_channel_with_discord_id_ok(self, mocker: MagicMock):
        channel_id = f'{fake.random_number(digits=18)}'
        self.instance.discord_channel_id = channel_id
        self.instance.save(update_fields=['discord_channel_id'])
        mocker.return_value = discord.channel_response(id=channel_id)

        serializer = self.serializer_class(self.instance)

        self.assertIsNotNone(serializer.data['discord_channel'])
