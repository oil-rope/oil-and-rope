import os
import pathlib
import random
import tempfile
import unittest
from datetime import timedelta
from unittest.mock import MagicMock, patch

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connection
from django.db.utils import DataError, IntegrityError
from django.test import TestCase
from django.utils import timezone, translation
from freezegun import freeze_time
from model_bakery import baker

from common.constants import models as constants
from registration.models import User
from roleplay.enums import DomainTypes, RoleplaySystems, SiteTypes
from roleplay.models import Campaign, Domain, Place, PlayerInCampaign, Race, Session, Trait, TraitType
from tests.mocks import discord
from tests.utils import fake

from ..utils import generate_place

connection_engine = connection.features.connection.settings_dict.get('ENGINE', None)


class TestTraitType(TestCase):
    def test_creation_without_required_ko(self):
        with self.assertRaisesRegex(IntegrityError, expected_regex=r'NOT NULL constraint failed: .+'):
            TraitType.objects.create()

    def test_creation_with_required_ok(self):
        trait_type = TraitType.objects.create(system=RoleplaySystems.PATHFINDER_1)
        trait = baker.make_recipe('roleplay.trait', type=trait_type)

        self.assertEqual(trait.type, trait_type)

    def test_str_ok(self):
        trait_type = TraitType.objects.create(
            name='Test TraitType', description='This is some description', system=RoleplaySystems.PATHFINDER_1,
        )

        self.assertEqual(f'Test TraitType [{trait_type.id}]', str(trait_type))

    def test_translation_ok(self):
        trait_type = TraitType.objects.get(name_en='Basic (Combat)')

        with translation.override('es'):
            self.assertEqual('Básicos (Combate)', trait_type.name)


class TestTrait(TestCase):
    def test_creation_without_required_ko(self):
        with self.assertRaisesRegex(IntegrityError, expected_regex=r'NOT NULL constraint failed: .+'):
            Trait.objects.create()

    def test_creation_with_required_ok(self):
        race: Race = baker.make_recipe('roleplay.race')
        Trait.objects.create(
            name=fake.word(),
            type=baker.make_recipe('roleplay.trait_type'),
            creator=baker.make_recipe('registration.user'),
            content_type=ContentType.objects.get_for_model(Race),
            object_id=race.id,
        )

        self.assertTrue(race.traits.all(), msg='Trait was not added to race.')

    def test_str_ok(self):
        race: Race = baker.make_recipe('roleplay.race')
        trait_type = TraitType.objects.create(name='Test TraitType', system=RoleplaySystems.DUNGEONS_AND_DRAGONS_35)
        trait = Trait.objects.create(
            name='Test Trait', type=trait_type, creator=baker.make_recipe('registration.user'),
            content_type=ContentType.objects.get_for_model(Race), object_id=race.id,
        )

        self.assertEqual(f'Test Trait (Dungeons & Dragons 3.5) [{trait.id}]', str(trait))


class TestDomain(TestCase):
    def test_str_ok(self):
        domain = baker.make(Domain)
        domain_type = DomainTypes(domain.domain_type)
        self.assertEqual(str(domain), f'{domain.name} [{domain_type.label.title()}]')

    def test_ok(self):
        entries = fake.pyint(min_value=1, max_value=100)
        baker.make(Domain, entries)
        self.assertEqual(entries, Domain.objects.count())

    @freeze_time('2020-01-01')
    def test_image_upload_ok(self):
        tmp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.jpg', dir='./tests/', delete=False)
        image_file = tmp_file.name
        with open(tmp_file.name, 'rb') as image_data:
            image = SimpleUploadedFile(name=image_file, content=image_data.read(), content_type='image/jpeg')

        place = baker.make(Domain)
        place.image = image
        place.save()
        expected_path = '/media/roleplay/domain/2020/01/01/{}/{}'.format(place.pk, image.name)
        expected_path = pathlib.Path(expected_path)
        self.assertIn(str(expected_path), place.image.path)

        tmp_file.close()
        os.unlink(tmp_file.name)
        os.unlink(place.image.path)

    @unittest.skipIf('sqlite3' in connection_engine, 'SQLite takes Varchar as Text')
    def test_max_name_length_ko(self):
        name = fake.password(length=26)
        with self.assertRaises(DataError) as ex:
            Domain.objects.create(name=name)
        self.assertRegex(str(ex.exception), r'.*value too long.*')

    def test_name_none_ko(self):
        with self.assertRaises(IntegrityError) as ex:
            Domain.objects.create(name=None)
        self.assertRegex(str(ex.exception), r'.*(null|NULL).*(constraint|CONSTRAINT).*')

    def test_is_domain_ok(self):
        instance = baker.make(Domain, domain_type=DomainTypes.DOMAIN)
        self.assertTrue(instance.is_domain)

    def test_is_domain_ko(self):
        instance = baker.make(Domain, domain_type=DomainTypes.SUBDOMAIN)
        self.assertFalse(instance.is_domain)

    def test_is_subdomain_ok(self):
        instance = baker.make(Domain, domain_type=DomainTypes.SUBDOMAIN)
        self.assertTrue(instance.is_subdomain)

    def test_is_subdomain_ko(self):
        instance = baker.make(Domain, domain_type=DomainTypes.DOMAIN)
        self.assertFalse(instance.is_subdomain)


class TestPlace(TestCase):
    model = Place

    def test_str_ok(self):
        place = generate_place()
        self.assertEqual(str(place), place.name)

    def test_ok(self):
        entries = fake.pyint(min_value=1, max_value=100)
        generate_place(entries)
        self.assertEqual(entries, self.model.objects.count())

    @freeze_time('2020-01-01')
    def test_image_upload_ok(self):
        tmp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.jpg', dir='./tests/', delete=False)
        image_file = tmp_file.name
        with open(tmp_file.name, 'rb') as image_data:
            image = SimpleUploadedFile(name=image_file, content=image_data.read(), content_type='image/jpeg')

        place = generate_place()
        place.image = image
        place.save()
        expected_path = '/media/roleplay/place/2020/01/01/{}/{}'.format(place.pk, image.name)
        expected_path = pathlib.Path(expected_path)
        self.assertIn(str(expected_path), place.image.path)

        tmp_file.close()
        os.unlink(tmp_file.name)
        os.unlink(place.image.path)

    def test_images_ok(self):
        images = []

        for _ in range(0, 3):
            tmp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.jpg', dir='./tests/', delete=False)
            image_file = tmp_file.name
            with open(tmp_file.name, 'rb') as image_data:
                image = SimpleUploadedFile(name=image_file, content=image_data.read(), content_type='image/jpeg')
            images.append(image)

            tmp_file.close()
            os.unlink(tmp_file.name)

        parent = None
        for image in images:
            place = generate_place(name=fake.country(), parent_site=parent)
            place.image = image
            place.save()
            parent = place

        obj_images = self.model.objects.first().images
        self.assertEqual(len(images), len(obj_images))

        for place in self.model.objects.all():
            os.unlink(place.image.path)

    @unittest.skipIf('sqlite3' in connection_engine, 'SQLite takes Varchar as Text')
    def test_max_name_length_ko(self):
        name = fake.password(length=101)
        with self.assertRaises(DataError) as ex:
            generate_place(name=name)
        self.assertRegex(str(ex.exception), r'.*value too long.*')

    def test_name_none_ko(self):
        with self.assertRaises(IntegrityError) as ex:
            generate_place(name=None)
        self.assertRegex(str(ex.exception), r'.*(null|NULL).*(constraint|CONSTRAINT).*')

    def test_resolve_icon(self):
        for site_type in self.model.ICON_RESOLVERS.keys():
            obj = generate_place(name=fake.country(), site_type=site_type)
            expected_url = '<i class="{}"></i>'.format(self.model.ICON_RESOLVERS.get(site_type, ''))
            self.assertEqual(expected_url, obj.resolve_icon())


class TestRace(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user: User = baker.make_recipe('registration.user')

    def test_create_without_owner_ko(self):
        with self.assertRaisesRegex(IntegrityError, expected_regex=r'NOT NULL constraint failed: .+'):
            Race.objects.create(name=fake.word())

    def test_clean_without_place_or_campaign_ko(self):
        with self.assertRaises(ValidationError) as ex:
            Race(owner_id=self.user.pk).clean()
        error_msg = ex.exception.message

        self.assertEqual(error_msg, 'Either a campaign or a place should be indicated.')

    def test_create_without_optional_ok(self):
        instance = Race.objects.create(
            owner_id=self.user.pk,
        )
        Race.objects.get(pk=instance.pk)

        self.assertTrue(True)


class TestCampaign(TestCase):
    model = Campaign

    @classmethod
    def setUpTestData(cls):
        # NOTE: This is done because it's better performance than creating a new entries each time
        cls.chat = baker.make_recipe('chat.chat')
        cls.world = generate_place(site_type=SiteTypes.WORLD)
        cls.owner = baker.make_recipe('registration.user')

    def setUp(self):
        self.name = fake.sentence(nb_words=3)
        self.instance: Campaign = self.model.objects.create(
            name=self.name, chat=self.chat, system=random.choice(RoleplaySystems.values), place=self.world,
            owner=self.owner,
        )

    def test_str_ok(self):
        expected = f'{self.name} [{self.instance.pk}]'

        self.assertEqual(expected, str(self.instance))

    def test_add_game_masters(self):
        game_masters = baker.make(constants.REGISTRATION_USER, 3)
        self.instance.add_game_masters(*game_masters)

        self.assertEqual(len(self.instance.game_masters), len(game_masters))

    def test_discord_channel_empty_is_none(self):
        self.assertIsNone(self.instance.discord_channel)

    @patch('bot.utils.discord_api_request')
    def test_discord_channel_ok(self, mocker_api_request: MagicMock):
        discord_id = f'{fake.random_number(digits=18)}'
        mocker_api_request.return_value = discord.channel_response(id=discord_id)
        self.instance.discord_channel_id = discord_id
        self.instance.save()

        self.assertIsNotNone(self.instance.discord_channel)

    def test_vote_ok(self):
        self.instance.vote(self.owner, True)
        instance = self.model.objects.with_votes().get(pk=self.instance.pk)

        self.assertEqual(instance.positive_votes, 1)

    def test_clean_start_date_greater_end_date_ko(self):
        self.instance.start_date = timezone.now() + timedelta(days=1)
        self.instance.end_date = timezone.now()

        with self.assertRaises(ValidationError) as ex:
            self.instance.clean()
        ex = ex.exception
        self.assertEqual('Start date must be before end date.', ex.message)

    def test_players_are_added_to_chat_ok(self):
        user_list = [user for user in baker.make_recipe('registration.user', 3)]
        self.instance.users.add(*user_list)
        chat = self.instance.chat

        for user in user_list:
            self.assertIn(user, chat.users.all())

    def test_players_are_removed_from_chat_ok(self):
        user_list = [user for user in baker.make_recipe('registration.user', 3)]
        self.instance.users.add(*user_list)
        chat = self.instance.chat
        user_to_remove = random.choice(user_list)
        self.instance.users.remove(user_to_remove)

        self.assertNotIn(user_to_remove, chat.users.all())


class TestPlayerInCampaign(TestCase):
    model = PlayerInCampaign

    @classmethod
    def setUpTestData(cls):
        cls.campaign = baker.make(constants.ROLEPLAY_CAMPAIGN)
        cls.user = baker.make(constants.REGISTRATION_USER)

    def test_str_ok(self):
        instance = self.model.objects.create(campaign=self.campaign, user=self.user)
        expected = f'{instance.user.username} in campaign {instance.campaign.name} (Game Master: False)'

        self.assertEqual(expected, str(instance))


class TestSession(TestCase):
    model = Session

    @classmethod
    def setUpTestData(cls):
        cls.campaign = baker.make_recipe('roleplay.campaign')

    def test_str_ok(self):
        name = fake.word()
        instance = self.model.objects.create(
            name=name,
            campaign=self.campaign,
        )
        expected = f'{name} [{instance.campaign.get_system_display()}]'

        self.assertEqual(expected, str(instance))
